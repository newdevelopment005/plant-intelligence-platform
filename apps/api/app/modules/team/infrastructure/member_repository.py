from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.team.domain.interfaces import TeamMemberRepositoryInterface
from app.modules.team.domain.models import TeamMemberModel


class TeamMemberRepository(TeamMemberRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_team_and_user(
        self, team_id: str, user_id: str
    ) -> TeamMemberModel | None:
        result = await self.db.execute(
            select(TeamMemberModel).where(
                TeamMemberModel.team_id == team_id,
                TeamMemberModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_member(self, member: TeamMemberModel) -> TeamMemberModel:
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def remove_member(self, team_id: str, user_id: str) -> bool:
        member = await self.get_by_team_and_user(team_id, user_id)
        if not member:
            return False
        await self.db.delete(member)
        await self.db.flush()
        return True

    async def list_members(self, team_id: str) -> list[TeamMemberModel]:
        result = await self.db.execute(
            select(TeamMemberModel)
            .where(TeamMemberModel.team_id == team_id)
            .order_by(TeamMemberModel.joined_at)
        )
        return list(result.scalars().all())
