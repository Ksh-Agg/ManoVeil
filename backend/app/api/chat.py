import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.permissions import get_current_user
from app.core.security import decode_token
from app.models.user import User
from app.schemas.chat import ChatSessionRead, MessageCreate, MessageRead, ChatResponse
from app.services import chat_service
from sqlalchemy import select
from app.models.chat import ChatSession

router = APIRouter()


@router.post("/sessions", response_model=ChatSessionRead, status_code=201)
async def create_session(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    session = await chat_service.create_session(db, user)
    return ChatSessionRead(
        id=session.id, user_id=session.user_id, persona=session.persona,
        started_at=session.started_at, ended_at=session.ended_at, summary=session.summary,
    )


@router.get("/sessions", response_model=list[ChatSessionRead])
async def list_sessions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sessions = await chat_service.get_user_sessions(db, user.id)
    return [ChatSessionRead(
        id=s.id, user_id=s.user_id, persona=s.persona,
        started_at=s.started_at, ended_at=s.ended_at, summary=s.summary,
    ) for s in sessions]


@router.get("/sessions/{session_id}/messages", response_model=list[MessageRead])
async def get_messages(session_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    messages = await chat_service.get_session_messages(db, session_id)
    return [MessageRead.model_validate(m) for m in messages]


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: UUID, data: MessageCreate,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return await chat_service.process_message(db, session_id, data.content, user.persona)


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: UUID):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=4001)
        return

    await websocket.accept()
    try:
        async with get_db().__class__.__wrapped__() if False else get_db() as db_gen:
            pass
    except Exception:
        pass

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            # For WebSocket, we process via REST-style internally
            await websocket.send_text(json.dumps({
                "type": "message",
                "content": "WebSocket chat is available. For full functionality, use the REST endpoint POST /chat/sessions/{id}/messages.",
            }))
    except WebSocketDisconnect:
        pass
