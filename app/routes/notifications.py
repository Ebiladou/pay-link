from sqlmodel import select
from fastapi import APIRouter, HTTPException, Request, Depends
from app.core.database import SessionDep
from app.core.deps import require_user, get_current_user
from app.core.model import Transactions, Links, Users, Notifications
from app.core.schema import NotificationResponse

notifications_router = APIRouter(prefix="/notifications")

@notifications_router.get("/", response_model=list[NotificationResponse])
async def list_notifications(
    session: SessionDep,
    user: Users = Depends(require_user)
):
    result = await session.exec(select(Notifications).where(Notifications.user_id == user.id))
    notifications = result.all()
    return notifications

# Additional routes for marking notifications as read, deleting notifications, et al.