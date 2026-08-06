from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.domain.interfaces import UserRepositoryInterface
from app.modules.auth.domain.models import UserModel


class UserRepository(UserRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> UserModel | None:
        result = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.db.execute(
            select(UserModel).where(UserModel.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def create(self, user: UserModel) -> UserModel:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: UserModel) -> UserModel:
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: str) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.flush()
        return True

    async def list_users(
        self, skip: int = 0, limit: int = 100, role: str | None = None
    ) -> list[UserModel]:
        query = select(UserModel)
        if role:
            query = query.where(UserModel.role == role)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_users(self) -> int:
        result = await self.db.execute(select(func.count(UserModel.id)))
        return result.scalar_one()

    async def search_by_email_or_name(self, query: str, limit: int = 10) -> list[UserModel]:
        search = f"%{query.lower().strip()}%"
        result = await self.db.execute(
            select(UserModel).where(
                (UserModel.email.ilike(search)) | (UserModel.full_name.ilike(search))
            ).limit(limit)
        )
        return list(result.scalars().all())
