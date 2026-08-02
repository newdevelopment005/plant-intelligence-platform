from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_assistant.domain.interfaces import ConversationRepositoryInterface
from app.modules.ai_assistant.domain.models import ConversationModel


class ConversationRepository(ConversationRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, conversation: ConversationModel) -> ConversationModel:
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: str) -> ConversationModel | None:
        result = await self.db.execute(
            select(ConversationModel).where(ConversationModel.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def list_conversations(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[ConversationModel]:
        query = select(ConversationModel)
        if project_id:
            query = query.where(ConversationModel.project_id == project_id)
        if status:
            query = query.where(ConversationModel.status == status)
        if search:
            query = query.where(ConversationModel.title.ilike(f"%{search}%"))
        if user_id:
            query = query.where(ConversationModel.created_by == user_id)
        query = query.order_by(ConversationModel.updated_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_conversations(
        self,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count()).select_from(ConversationModel)
        if project_id:
            query = query.where(ConversationModel.project_id == project_id)
        if status:
            query = query.where(ConversationModel.status == status)
        if search:
            query = query.where(ConversationModel.title.ilike(f"%{search}%"))
        if user_id:
            query = query.where(ConversationModel.created_by == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update(self, conversation: ConversationModel) -> ConversationModel:
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def delete(self, conversation_id: str) -> bool:
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        await self.db.delete(conversation)
        return True

    async def increment_message_count(self, conversation_id: str) -> None:
        conversation = await self.get_by_id(conversation_id)
        if conversation:
            conversation.message_count = (conversation.message_count or 0) + 1
            await self.db.flush()
