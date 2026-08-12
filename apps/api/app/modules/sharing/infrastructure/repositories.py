import uuid as _uuid
from datetime import UTC, datetime

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sharing.domain.interfaces import ShareRecipientRepositoryInterface, ShareRepositoryInterface
from app.modules.sharing.domain.models import ShareModel, ShareRecipientModel


class ShareRepository(ShareRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, share: ShareModel) -> ShareModel:
        self.db.add(share)
        await self.db.flush()
        await self.db.refresh(share)
        return share

    async def get_by_id(self, share_id: str) -> ShareModel | None:
        result = await self.db.execute(
            select(ShareModel).where(ShareModel.id == share_id)
        )
        return result.scalar_one_or_none()

    async def get_by_token(self, token: str) -> ShareModel | None:
        result = await self.db.execute(
            select(ShareModel).where(ShareModel.share_token == token)
        )
        return result.scalar_one_or_none()

    async def list_my_shares(self, owner_id: str) -> list[ShareModel]:
        result = await self.db.execute(
            select(ShareModel)
            .where(ShareModel.owner_id == owner_id)
            .order_by(ShareModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, share_id: str) -> bool:
        result = await self.db.execute(
            delete(ShareModel).where(ShareModel.id == share_id)
        )
        return result.rowcount > 0


class ShareRecipientRepository(ShareRecipientRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, recipient: ShareRecipientModel) -> ShareRecipientModel:
        self.db.add(recipient)
        await self.db.flush()
        await self.db.refresh(recipient)
        return recipient

    async def create_many(self, recipients: list[ShareRecipientModel]) -> list[ShareRecipientModel]:
        self.db.add_all(recipients)
        await self.db.flush()
        for r in recipients:
            await self.db.refresh(r)
        return recipients

    async def list_by_share(self, share_id: str) -> list[ShareRecipientModel]:
        result = await self.db.execute(
            select(ShareRecipientModel)
            .where(ShareRecipientModel.share_id == share_id)
        )
        return list(result.scalars().all())

    async def list_shared_with_user(
        self,
        user_id: str,
        team_ids: list[str] | None = None,
        department_ids: list[str] | None = None,
    ) -> list[ShareRecipientModel]:
        stmt = select(ShareRecipientModel).order_by(ShareRecipientModel.shared_at.desc())
        conditions = [
            ShareRecipientModel.recipient_type == "user",
            ShareRecipientModel.user_id == user_id,
        ]
        if team_ids:
            conditions.append(
                (ShareRecipientModel.recipient_type == "team")
                & ShareRecipientModel.team_id.in_(team_ids)
            )
        if department_ids:
            conditions.append(
                (ShareRecipientModel.recipient_type == "department")
                & ShareRecipientModel.department_id.in_(department_ids)
            )
        result = await self.db.execute(stmt.where(or_(*conditions)))
        return list(result.scalars().all())

    async def list_user_memberships(self, user_id: str) -> dict:
        from app.modules.auth.domain.models import UserModel
        from app.modules.team.domain.models import TeamMemberModel

        team_result = await self.db.execute(
            select(TeamMemberModel.team_id).where(TeamMemberModel.user_id == user_id)
        )
        team_ids = [str(t) for t in team_result.scalars().all()]

        user_result = await self.db.execute(
            select(UserModel.department_id).where(UserModel.id == user_id)
        )
        department_id = user_result.scalar_one_or_none()

        return {
            "team_ids": team_ids,
            "department_ids": [str(department_id)] if department_id else [],
        }

    async def delete_by_share(self, share_id: str) -> bool:
        result = await self.db.execute(
            delete(ShareRecipientModel).where(ShareRecipientModel.share_id == share_id)
        )
        return result.rowcount > 0
