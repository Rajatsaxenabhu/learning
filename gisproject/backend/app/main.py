from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.service.agent.runtime import AgentRuntime

from app.api.routes import app_router
from app.conf.logging.applog import logger
from app.conf.redis.redis_async_manager import async_redis_manager
from app.conf.redis.redis_conf import close_redis
from app.middleware.middleware import setup_logging_middleware


agent_runtime = AgentRuntime()


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting application...")

    await async_redis_manager.initialize()
    logger.info("Redis ready")

    await agent_runtime.initialize()
    logger.info("Agent runtime ready")

    app.state.agent_runtime = agent_runtime

    yield

    logger.info("Shutting down application...")

    await agent_runtime.close()
    logger.info("Agent runtime closed")

    await close_redis()


app = FastAPI(
    title="Decision support system",
    version="2.0.0",
    lifespan=lifespan,
)


setup_logging_middleware(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://kalki.space",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    app_router,
    prefix="/api",
)