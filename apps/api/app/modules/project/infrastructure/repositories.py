from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.project.domain.interfaces import ProjectRepositoryInterface
from app.modules.project.domain.models import ProjectModel


class ProjectRepository(ProjectRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_id: str) -> ProjectModel | None:
        result = await self.db.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        return result.scalar_one_or_none()

    async def create(self, project: ProjectModel) -> ProjectModel:
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def update(self, project: ProjectModel) -> ProjectModel:
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def delete(self, project_id: str) -> bool:
        project = await self.get_by_id(project_id)
        if not project:
            return False
        await self.db.delete(project)
        await self.db.flush()
        return True

    async def list_by_owner(
        self, owner_id: str, skip: int = 0, limit: int = 100
    ) -> list[ProjectModel]:
        result = await self.db.execute(
            select(ProjectModel)
            .where(ProjectModel.owner_id == owner_id)
            .order_by(ProjectModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_by_member(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[ProjectModel]:
        from app.modules.project.domain.models import ProjectMemberModel

        result = await self.db.execute(
            select(ProjectModel)
            .join(ProjectMemberModel, ProjectMemberModel.project_id == ProjectModel.id)
            .where(ProjectMemberModel.user_id == user_id)
            .order_by(ProjectModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_all(
        self, skip: int = 0, limit: int = 100, status: str | None = None
    ) -> list[ProjectModel]:
        query = select(ProjectModel)
        if status:
            query = query.where(ProjectModel.status == status)
        query = query.order_by(ProjectModel.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_owner(self, owner_id: str) -> int:
        result = await self.db.execute(
            select(func.count(ProjectModel.id)).where(
                ProjectModel.owner_id == owner_id
            )
        )
        return result.scalar_one()

    async def count_by_member(self, user_id: str) -> int:
        from app.modules.project.domain.models import ProjectMemberModel

        result = await self.db.execute(
            select(func.count(ProjectModel.id))
            .join(ProjectMemberModel, ProjectMemberModel.project_id == ProjectModel.id)
            .where(ProjectMemberModel.user_id == user_id)
        )
        return result.scalar_one()

    async def count_all(self, status: str | None = None) -> int:
        query = select(func.count(ProjectModel.id))
        if status:
            query = query.where(ProjectModel.status == status)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def search(
        self, query: str, user_id: str | None = None, skip: int = 0, limit: int = 100
    ) -> list[ProjectModel]:
        from app.modules.project.domain.models import ProjectMemberModel

        q = select(ProjectModel).where(
            or_(
                ProjectModel.name.ilike(f"%{query}%"),
                ProjectModel.description.ilike(f"%{query}%"),
            )
        )

        if user_id:
            q = q.join(
                ProjectMemberModel, ProjectMemberModel.project_id == ProjectModel.id
            ).where(ProjectMemberModel.user_id == user_id)

        q = q.order_by(ProjectModel.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(q)
        return list(result.scalars().all())
