import uuid
from typing import List

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import MessagePublic, MessageCreate, Message

router = APIRouter()

@router.post("/", response_model=MessagePublic)
def send_message(
    message: MessageCreate,
    current_user: CurrentUser,
    db: SessionDep,
) -> MessagePublic:
    db_message = Message.model_validate(message, update={"sender_id": current_user.id})
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/conversation/{user_id}", response_model=List[MessagePublic])
def get_conversation(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    db: SessionDep 
) -> List[MessagePublic]:
    query = select(Message).where(
        (Message.sender_id == current_user.id) & (Message.receiver_id == user_id) |
        (Message.sender_id == user_id) & (Message.receiver_id == current_user.id)
    )
    messages = db.exec(query).all()
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found")
    return messages