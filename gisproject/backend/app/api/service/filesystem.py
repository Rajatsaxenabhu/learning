import json
import re
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, Tuple

from fastapi import HTTPException, UploadFile

from app.conf.redis.redis_async_manager import AsyncRedisManager
from app.conf.settings import Settings

UPLOAD_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
STORAGE_TTL_SECONDS = 60 * 60


class FileUpload:
    def __init__(self):
        self.temp_dir = Path(Settings().TEMP_DIR)
        self.input_dir = self.temp_dir / "input" 
        self.output_dir = self.temp_dir / "output" 
        self.chunk_dir = self.temp_dir / "chunk_dir"
        for directory in (self.input_dir, self.output_dir, self.chunk_dir):
            directory.mkdir(parents=True, exist_ok=True)
        self.MAX_SIZE_BYTES = 500 * 1024 * 1024
        self.redis = AsyncRedisManager()

    def _upload_dir(self, upload_id: str) -> Path:
        if not UPLOAD_ID_RE.match(upload_id):
            raise HTTPException(status_code=400, detail="Invalid upload_id")
        return self.chunk_dir / upload_id

    async def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        dataset = await self.redis.get_json(dataset_id)
        if not dataset:
            raise ValueError("Invalid or expired dataset_id")
        return dataset

    async def _get_file_path(self, dataset_id: str) -> Path:
        file_path = Path((await self.get_dataset(dataset_id))["path"])
        if file_path.exists():
            return file_path
        raise FileNotFoundError("Temporary file missing")

    @staticmethod
    def format_file_size(size_bytes: int) -> Dict[str, Any]:
        if size_bytes < 1024:
            return {"value": size_bytes, "unit": "B"}
        if size_bytes < 1024**2:
            return {"value": round(size_bytes / 1024, 2), "unit": "KB"}
        if size_bytes < 1024**3:
            return {"value": round(size_bytes / 1024**2, 2), "unit": "MB"}
        return {"value": round(size_bytes / 1024**3, 2), "unit": "GB"}

    async def chunk_upload(
        self, file: UploadFile, upload_id: str, chunk_index: int
    ) -> str:
        if chunk_index < 0:
            raise HTTPException(status_code=400, detail="Invalid chunk_index")

        chunk_dir = self._upload_dir(upload_id)
        chunk_dir.mkdir(parents=True, exist_ok=True)
        chunk_path = chunk_dir / f"{chunk_index}.part"

        current_size = sum(
            f.stat().st_size for f in chunk_dir.glob("*.part") if f != chunk_path
        )

        try:
            with chunk_path.open("wb") as buffer:
                while True:
                    data = await file.read(1024 * 1024)
                    if not data:
                        break
                    current_size += len(data)
                    if current_size > self.MAX_SIZE_BYTES:
                        raise HTTPException(
                            status_code=413, detail="File exceeds 500MB limit"
                        )
                    buffer.write(data)
        except HTTPException:
            shutil.rmtree(chunk_dir, ignore_errors=True)
            raise
        except Exception:
            shutil.rmtree(chunk_dir, ignore_errors=True)
            raise HTTPException(status_code=500, detail="Failed to write chunk")
        return "Chunk uploaded successfully"

    async def _build_merge(
        self, upload_id: str, filename: str, total_chunks: int
    ) -> Tuple[str, Path]:
        chunk_dir = self._upload_dir(upload_id)
        if not chunk_dir.exists():
            raise HTTPException(status_code=404, detail="Upload not found")

        dataset_id = f"ds_{uuid.uuid4().hex[:12]}"
        dataset_dir = self.input_dir / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)
        file_path = dataset_dir / filename

        try:
            with file_path.open("wb") as output_file:
                for i in range(total_chunks):
                    chunk_file = chunk_dir / f"{i}.part"
                    if not chunk_file.exists():
                        raise HTTPException(
                            status_code=400, detail=f"Missing chunk {i}"
                        )
                    with chunk_file.open("rb") as cf:
                        shutil.copyfileobj(cf, output_file)
        except Exception:
            shutil.rmtree(dataset_dir, ignore_errors=True)
            raise

        shutil.rmtree(chunk_dir, ignore_errors=True)
        return dataset_id, file_path

    async def merge_chunks(
        self, upload_id: str, filename: str, total_chunks: int
    ) -> Dict[str, Any]:
        filename = Path(filename).name
        if not filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        if total_chunks < 1:
            raise HTTPException(status_code=400, detail="Invalid total_chunks")

        dataset_id, file_path = await self._build_merge(
            upload_id, filename, total_chunks
        )
        file_ext = file_path.suffix.lower()
        dataset = {
            "dataset_id": dataset_id,
            "filename": filename,
            "path": str(file_path),
            "format": file_ext.lstrip(".") or "unknown",
        }
        await self.redis.set(dataset_id, json.dumps(dataset), ex=STORAGE_TTL_SECONDS)
        return {"dataset_id": dataset_id}
