from typing import Any, Dict, Tuple

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from app.api.service.agenttalk import UserAgent
from app.api.service.filesystem import FileUpload
from app.api.service.model import UserModel
from app.conf.logging.applog import logger
from app.conf.ws_config import connection_manager, safe_send

user_model = UserModel()

SESSION_NOT_FOUND = 4404
INTERNAL_ERROR = 1011


class ChatConnection:

    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id

    async def send(self, message: dict):
        await safe_send(self.websocket, message)

    async def broadcast(self, message: dict):
        await connection_manager.broadcast(self.session_id, message)

    async def send_error(self, detail: str):
        await self.send({"type": "error", "detail": detail})

    async def send_connected(self):
        await self.send(
            {
                "type": "connected",
                "session_id": self.session_id,
                "total_tokens": await user_model.get_tokens(self.session_id),
            }
        )

    async def read_question(self) -> Tuple[str | None, Dict[str, Any] | None]:
        data = await self.websocket.receive_json()
        question = None
        if isinstance(data, dict):
            question = str(data.get("message", "")).strip() or None
        if question is None:
            await self.send_error("message is required")
            return None, None
        dataset_id = data.get("dataset_id")
        if not dataset_id:
            return question, None
        try:
            dataset = await FileUpload().get_dataset(str(dataset_id))
        except ValueError as exc:
            await self.send_error(str(exc))
            return None, None
        return question, dataset

    async def approve_tools(self, payload: dict) -> bool:
        await self.send({"type": "tool_approval", **payload})
        reply = await self.websocket.receive_json()
        return isinstance(reply, dict) and bool(reply.get("approve"))

    async def send_token(self, text: str):
        await self.broadcast({"type": "token", "content": text})

    async def answer(
        self, agent: UserAgent, question: str, dataset: Dict[str, Any] | None
    ):
        try:
            used = await agent.ask(
                question, self.send_token, self.approve_tools, dataset
            )
        except WebSocketDisconnect:
            raise
        except Exception:
            logger.exception(f"agent[{self.session_id}] failed")
            await self.send_error("agent failed")
            return

        total = await user_model.add_tokens(self.session_id, used)
        await self.broadcast({"type": "usage", "used": used, "total": total})
        await self.broadcast({"type": "done"})

    async def run(self):
        await self.websocket.accept()
        await connection_manager.connect(self.websocket, self.session_id)
        try:
            async with UserAgent(self.session_id) as agent:
                await self.send_connected()
                while True:
                    question, dataset = await self.read_question()
                    if question is None:
                        continue
                    await self.answer(agent, question, dataset)
        except WebSocketDisconnect:
            logger.debug(f"ws[{self.session_id}] disconnected")
        except Exception:
            await self.handle_failure()
        finally:
            await connection_manager.disconnect(self.websocket, self.session_id)

    async def handle_failure(self):
        if self.websocket.client_state != WebSocketState.CONNECTED:
            logger.debug(f"ws[{self.session_id}] disconnected")
            return
        logger.exception(f"ws[{self.session_id}] agent unavailable")
        await self.send_error("agent unavailable")
        await self.websocket.close(code=INTERNAL_ERROR)
