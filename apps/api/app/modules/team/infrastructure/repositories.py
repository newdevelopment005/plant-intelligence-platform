from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.team.domain.interfaces import TeamRepositoryInterface
from app.modules.team.domain.models import TeamModel


class TeamRepository(TeamRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, team_id: str) -> TeamModel | None:
        result = await self.db.execute(
            select(TeamModel).where(TeamModel.id == team_id)
        )
        return result.scalar_one_or_none()

    async def create(self, team: TeamModel) -> TeamModel:
        self.db.add(team)
        await self.db.flush()
        await self.db.refresh(team)
        return team

    async def delete(self, team_id: str) -> bool:
        team = await self.get_by_id(team_id)
        if not team:
            return False
        await self.db.delete(team)
        await self.db.flush()
        return True

    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[TeamModel]:
        from app.modules.team.domain.models import TeamMemberModel

        result = await self.db.execute(
            select(TeamModel)
            .join(TeamMemberModel, TeamMemberModel.team_id == TeamModel.id)
            .where(TeamMemberModel.user_id == user_id)
            .order_by(TeamModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
