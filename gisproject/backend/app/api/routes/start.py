from fastapi import APIRouter,status
from app.conf.settings import Settings
from app.utils.externalapi import get_api
from app.utils.exception import validate
from app.api.routes.service.model import UserModel
router = APIRouter()
user_model = UserModel()


@router.get("/ready",status_code=status.HTTP_200_OK)
@validate
async def ready():
    resp = await get_api(f"{Settings().LLM_URL}/v1/models", timeout=5.0)
    session = await user_model.add_session(resp)

    return {
        "status": "ready",
        "vllm": "ready",
        **session,
    }
