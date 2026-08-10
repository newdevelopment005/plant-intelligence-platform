from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.department.domain.interfaces import (
    DepartmentMemberRepositoryInterface,
    DepartmentRepositoryInterface,
)
from app.modules.department.domain.models import DepartmentMemberModel, DepartmentModel


class DepartmentRepository(DepartmentRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, department_id: str) -> DepartmentModel | None:
        result = await self.db.execute(
            select(DepartmentModel).where(DepartmentModel.id == department_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        include_inactive: bool = False,
    ) -> list[DepartmentModel]:
        stmt = select(DepartmentModel)
        if search:
            stmt = stmt.where(
                or_(
                    DepartmentModel.name.ilike(f"%{search}%"),
                    DepartmentModel.code.ilike(f"%{search}%"),
                )
            )
        if not include_inactive:
            stmt = stmt.where(DepartmentModel.is_active.is_(True))
        stmt = stmt.order_by(DepartmentModel.name.asc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_all(self, search: str | None = None) -> int:
        stmt = select(func.count(DepartmentModel.id)).where(
            DepartmentModel.is_active.is_(True)
        )
        if search:
            stmt = stmt.where(
                or_(
                    DepartmentModel.name.ilike(f"%{search}%"),
                    DepartmentModel.code.ilike(f"%{search}%"),
                )
            )
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def create(self, department: DepartmentModel) -> DepartmentModel:
        self.db.add(department)
        await self.db.flush()
        await self.db.refresh(department)
        return department

    async def update(self, department: DepartmentModel) -> DepartmentModel:
        department.updated_at = datetime.now(UTC)
        await self.db.flush()
        await self.db.refresh(department)
        return department

    async def delete(self, department_id: str) -> bool:
        department = await self.get_by_id(department_id)
        if not department:
            return False
        await self.db.delete(department)
        await self.db.flush()
        return True


class DepartmentMemberRepository(DepartmentMemberRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_department_and_user(
        self, department_id: str, user_id: str
    ) -> DepartmentMemberModel | None:
        result = await self.db.execute(
            select(DepartmentMemberModel).where(
                DepartmentMemberModel.department_id == department_id,
                DepartmentMemberModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_member(self, member: DepartmentMemberModel) -> DepartmentMemberModel:
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def update_role(
        self, department_id: str, user_id: str, role: str
    ) -> DepartmentMemberModel | None:
        member = await self.get_by_department_and_user(department_id, user_id)
        if not member:
            return None
        member.role = role
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def remove_member(self, department_id: str, user_id: str) -> bool:
        member = await self.get_by_department_and_user(department_id, user_id)
        if not member:
            return False
        await self.db.delete(member)
        await self.db.flush()
        return True

    async def list_members(self, department_id: str) -> list[DepartmentMemberModel]:
        result = await self.db.execute(
            select(DepartmentMemberModel)
            .where(DepartmentMemberModel.department_id == department_id)
            .order_by(DepartmentMemberModel.joined_at)
        )
        return list(result.scalars().all())