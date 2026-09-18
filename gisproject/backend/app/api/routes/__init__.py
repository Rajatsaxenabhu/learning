from fastapi import APIRouter

from app.api.routes.start import router as start_router

app_router = APIRouter()
app_router.include_router(start_router)
