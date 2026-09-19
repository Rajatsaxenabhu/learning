from fastapi import APIRouter, File, Header, UploadFile, status
from pydantic import BaseModel
from app.conf.settings import Settings
from app.utils.externalapi import get_api
from app.utils.exception import validate
from app.api.service.filesystem import FileUpload
from app.api.service.model import UserModel
from app.api.schema import Chunkcomplete
router = APIRouter()




@router.get("/ready",status_code=status.HTTP_200_OK)
@validate
async def ready():
    user_model = UserModel()
    resp = await get_api(f"{Settings().LLM_URL}/v1/models", timeout=5.0)
    session = await user_model.add_session(resp)

    return {
        "status": "ready",
        "vllm": "ready",
        **session,
    }


@router.post("/upload_data_chunk",status_code=status.HTTP_201_CREATED)
@validate
async def upload_data_chunk(
    file: UploadFile = File(...),
    upload_id: str = Header(...),
    chunk_index: int = Header(...),
    
):
    return await FileUpload().chunk_upload(file,upload_id,chunk_index)   


@router.post("/upload/complete",status_code=status.HTTP_201_CREATED)
@validate
async def complete_upload(payload:Chunkcomplete):
    """   Merge all chunks into final file.  """
    return await FileUpload().merge_chunks(payload.upload_id,payload.filename,payload.total_chunks)