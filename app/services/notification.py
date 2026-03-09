from app.core.logger import logger
from app.core.database import SessionDep
from app.core.model import Users, Transactions
from app.core.model import Notifications

class NotificationService:
    async def transaction_success(
        self,
        session: SessionDep,
        user: Users,
        transaction: Transactions,
    ):

        message = f"You received {transaction.amount} on reference {transaction.reference}."

        notification = Notifications(
            user_id=user.id,
            message=message
        )
        
        session.add(notification)
        await session.commit()

        return True

notification_service = NotificationService()