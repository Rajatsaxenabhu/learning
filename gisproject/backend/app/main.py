from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import app_router
from contextlib import asynccontextmanager
from app.conf.logging.applog import logger
from app.middleware.middleware import setup_logging_middleware
from app.conf.redis.redis_async_manager import async_redis_manager
from app.conf.redis.redis_conf import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")

    await async_redis_manager.initialize()
    logger.info("Redis ready")

    yield

    logger.info("Shutting down application...")
    await close_redis()


app = FastAPI(
    title="Decision support system", 
    version="2.0.0",
    lifespan=lifespan
)


setup_logging_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(app_router, prefix="/api")



