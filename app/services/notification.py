from app.core.logger import logger
from app.core.database import SessionDep
from app.core.model import Users, Transactions
from app.core.model import Notifications
from sqlmodel import select

class NotificationService:
    async def transaction_success(self, session: SessionDep, user: Users, transaction: Transactions,):

        message = f"You received {transaction.amount} NGN from {transaction.email} for reference {transaction.reference}."

        result = await session.exec(select(Notifications).where(Notifications.user_id == user.id, Notifications.transaction_id == transaction.id))
        existing_notification = result.first()

        if existing_notification is None:
            notification = Notifications(
                user_id=user.id,
                transaction_id=transaction.id,
                message=message
            )

            session.add(notification)
            await session.commit()

        return True

notification_service = NotificationService()