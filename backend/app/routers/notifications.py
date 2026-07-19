from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.authorization import require_authentication
from app.db.session import get_db
from app.schemas.notification import NotificationResponse, NotificationUpdate
from app.db.models import Notification

router = APIRouter(tags=["Notifications"])


@router.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(
    db: Session = Depends(get_db), 
    user = Depends(require_authentication),
    is_read: Optional[bool] = None
):
    query = db.query(Notification).filter(Notification.user_id == user.id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    return query.order_by(Notification.created_at.desc()).all()


@router.put("/notifications/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int, 
    payload: NotificationUpdate, 
    db: Session = Depends(get_db), 
    user = Depends(require_authentication)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id, 
        Notification.user_id == user.id
    ).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(notification, key, value)
    db.commit()
    db.refresh(notification)
    return notification


@router.post("/notifications/mark-all", response_model=dict)
def mark_all_read(db: Session = Depends(get_db), user = Depends(require_authentication)):
    db.query(Notification).filter(
        Notification.user_id == user.id, 
        Notification.is_read == False
    ).update({Notification.is_read: True})
    db.commit()
    return {"success": True}


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int, 
    db: Session = Depends(get_db), 
    user = Depends(require_authentication)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id, 
        Notification.user_id == user.id
    ).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    db.delete(notification)
    db.commit()
