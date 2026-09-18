import asyncio
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from app.conf.redis.redis_async_manager import async_redis_manager
from app.conf.settings import Settings
from app.conf.logging.applog import logger
TEMP_DIR = Path(Settings().TEMP_DIR)

CLEANUP_LOCK_KEY = "lock:clean_temp_folder"
CLEANUP_LOCK_TTL_SECONDS = 3600 


async def clean_temp_folder_daily():
    while True:
        now = datetime.now()

        next_run = now.replace(hour=4, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)
        await asyncio.sleep((next_run - now).total_seconds())
        try:
            got_lock = await async_redis_manager.client().set(
                CLEANUP_LOCK_KEY, "1", nx=True, ex=CLEANUP_LOCK_TTL_SECONDS
            )
            if not got_lock:
                continue

            if TEMP_DIR.exists():
                for item in TEMP_DIR.iterdir():
                    try:
                        if item.is_file() or item.is_symlink():
                            item.unlink()  # Delete file
                        elif item.is_dir():
                            shutil.rmtree(item)  # Delete subfolder
                    except Exception as e:
                        logger.error(f"Failed to delete {item}: {e}")

            logger.info("Temp folder cleaned.")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")



