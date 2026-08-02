from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_assistant.domain.interfaces import MessageRepositoryInterface
from app.modules.ai_assistant.domain.models import MessageModel


class MessageRepository(MessageRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, message: MessageModel) -> MessageModel:
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_by_id(self, message_id: str) -> MessageModel | None:
        result = await self.db.execute(
            select(MessageModel).where(MessageModel.id == message_id)
        )
        return result.scalar_one_or_none()

    async def list_by_conversation(
        self, conversation_id: str, skip: int = 0, limit: int = 100
    ) -> list[MessageModel]:
        query = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_conversation(self, conversation_id: str) -> int:
        query = (
            select(func.count())
            .select_from(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def delete(self, message_id: str) -> bool:
        result = await self.db.execute(
            select(MessageModel).where(MessageModel.id == message_id)
        )
        message = result.scalar_one_or_none()
        if not message:
            return False
        await self.db.delete(message)
        return True
