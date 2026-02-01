from datetime import datetime, timedelta
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import engine
from app.core.model import Users
from app.core.logger import logger
from sqlalchemy.orm import sessionmaker

async def cleanup_deleted_users():
    logger.info("Running deleted users cleanup")
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            cleanup_time = datetime.now() - timedelta(days=30)
            
            result = await session.exec(select(Users).where(
                Users.deletion_requested == True,
                Users.updated_at <= cleanup_time
            ))
            delete_users = result.all()
            
            if not delete_users:
                logger.info("No users found for deletion")
                return
            
            deleted_count = 0
            for user in delete_users:
                await session.delete(user)
                deleted_count += 1
            
            await session.commit()
            logger.info(f"Successfully deleted {deleted_count} users")
            
        except Exception as e:
            logger.error(f"Error during user cleanup: {e}")
            await session.rollback()