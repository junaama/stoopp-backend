import uuid
from typing import List

from fastapi import APIRouter, HTTPException
from sqlmodel import  select

from app.api.deps import CurrentUser, SessionDep
from app.models import Notification, NotificationCreate, NotificationPublic

router = APIRouter()

@router.post("/", response_model=NotificationPublic)
def create_notification(
    notification: NotificationCreate,
    db: SessionDep,
) -> NotificationPublic:
    db_notification = Notification.model_validate(notification)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.get("/", response_model=List[NotificationPublic])
def get_notifications(
    db: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
) -> List[NotificationPublic]:
    query = select(Notification).where(Notification.user_id == current_user.id).offset(skip).limit(limit)
    notifications = db.exec(query).all()
    return notifications

@router.patch("/{notification_id}", response_model=NotificationPublic)
def mark_notification_as_read(
    notification_id: uuid.UUID,
    db: SessionDep,
    current_user: CurrentUser
) -> NotificationPublic:
    db_notification = db.get(Notification, notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if db_notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this notification")
    db_notification.is_read = True
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification