import uuid
from app.conf.redis.redis_async_manager import async_redis_manager


class UserModel:
    SESSION_TTL = 60 * 60 * 24

    async def add_session(self, resp):
        redis = async_redis_manager.client()

        session_id = uuid.uuid4().hex
        key = f"session:{session_id}"
        model = resp["data"][0]["id"]

        await redis.hset(key, mapping={"model": model, "token": 0})
        await redis.expire(key, self.SESSION_TTL)
        return {
            "session_id": session_id,
            "model": model,
        }

    async def get_model(self, session_id: str) -> str | None:
        redis = async_redis_manager.client()
        model = await redis.hget(f"session:{session_id}", "model")
        return model.decode() if isinstance(model, bytes) else model

    async def add_tokens(self, session_id: str, used: int) -> int:
        redis = async_redis_manager.client()
        return int(await redis.hincrby(f"session:{session_id}", "token", used))

    async def get_tokens(self, session_id: str) -> int:
        redis = async_redis_manager.client()
        return int(await redis.hget(f"session:{session_id}", "token") or 0)
