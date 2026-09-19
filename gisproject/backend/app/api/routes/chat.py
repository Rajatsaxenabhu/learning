from fastapi import APIRouter, WebSocket

from app.api.routes.service.chat import SESSION_NOT_FOUND, ChatConnection, user_model

router = APIRouter()


@router.websocket("/ws/start/{session_id}")
async def chat_ws(websocket: WebSocket, session_id: str):
    if not await user_model.get_model(session_id):
        await websocket.close(code=SESSION_NOT_FOUND)
        return

    await ChatConnection(websocket, session_id).run()
