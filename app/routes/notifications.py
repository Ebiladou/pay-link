from sqlmodel import select
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func
from app.core.database import SessionDep
from app.core.deps import require_user
from app.core.model import Users, Notifications
from app.core.schema import NotificationResponse, AggNotificationResponse
from datetime import datetime
from typing import Optional

notifications_router = APIRouter(prefix="/notifications")

@notifications_router.get("/{id}", response_model=NotificationResponse)
async def get_notification(id: int, session: SessionDep, user: Users = Depends(require_user)):
    result = await session.exec(select(Notifications).where(Notifications.id == id, Notifications.user_id == user.id))
    notification = result.first()

    if notification is None:
        raise HTTPException(
            status_code=404, 
            detail="Notification not found"
        )

    if notification.is_read is False:
        notification.is_read = True
        notification.updated_at = datetime.now()

        session.add(notification)
        await session.commit()

    return notification

@notifications_router.get("/", response_model=AggNotificationResponse)
async def list_notifications(session: SessionDep, page_number: int = 1, page_size: int = 10, is_read: Optional[bool] = None, user: Users = Depends(require_user)):
    query = select(Notifications).where(Notifications.user_id == user.id)

    if is_read is not None:
        query = query.where(Notifications.is_read == is_read)

    total_count = await session.exec(select(func.count()).select_from(query.subquery()))
    total = total_count.one()

    offset = (page_number - 1) * page_size
    paginated_query = query.offset(offset).limit(page_size)

    result = await session.exec(paginated_query)
    notifications = result.all()

    if notifications == []:
        raise HTTPException(
            status_code=404, 
            detail="No notifications found"
        )

    return AggNotificationResponse(
        total=total,
        data=notifications
    )