from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.project.domain.interfaces import ProjectMemberRepositoryInterface
from app.modules.project.domain.models import ProjectMemberModel


class ProjectMemberRepository(ProjectMemberRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_project_and_user(
        self, project_id: str, user_id: str
    ) -> ProjectMemberModel | None:
        result = await self.db.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_member(self, member: ProjectMemberModel) -> ProjectMemberModel:
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def update_member_role(
        self, project_id: str, user_id: str, role: str
    ) -> ProjectMemberModel | None:
        member = await self.get_by_project_and_user(project_id, user_id)
        if not member:
            return None
        member.role = role
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def remove_member(self, project_id: str, user_id: str) -> bool:
        member = await self.get_by_project_and_user(project_id, user_id)
        if not member:
            return False
        await self.db.delete(member)
        await self.db.flush()
        return True

    async def list_members(self, project_id: str) -> list[ProjectMemberModel]:
        result = await self.db.execute(
            select(ProjectMemberModel)
            .where(ProjectMemberModel.project_id == project_id)
            .order_by(ProjectMemberModel.joined_at)
        )
        return list(result.scalars().all())

    async def count_members(self, project_id: str) -> int:
        result = await self.db.execute(
            select(func.count(ProjectMemberModel.id)).where(
                ProjectMemberModel.project_id == project_id
            )
        )
        return result.scalar_one()
