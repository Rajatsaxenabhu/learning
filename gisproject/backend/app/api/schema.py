
from pydantic import BaseModel
class Chunkcomplete(BaseModel):
    upload_id: str
    total_chunks: int
    filename: str
