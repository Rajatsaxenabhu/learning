from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import app_router

from app.middleware.middleware import setup_logging_middleware


# @asynccontextmanager
# async def lifespan(app: FastAPI):

#     logger.info("Starting application...")

#     await async_redis_manager.initialize()
#     logger.info("Redis ready")

#     await initialize_visits_if_absent()

    
#     asyncio.create_task(clean_temp_folder_daily())
#     asyncio.create_task(refresh_visits_loop())
#     logger.info(" background task starts")
#     yield


#     logger.info("Shutting down application...")
#     await close_redis() 

app = FastAPI(
    title="Decision support system", 
    version="2.0.0",
    # lifespan=lifespan
)


setup_logging_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(app_router, prefix="/api")



