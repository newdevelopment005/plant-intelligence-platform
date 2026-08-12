import uuid as _uuid
from datetime import UTC, datetime

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.sharing.domain.interfaces import ShareRecipientRepositoryInterface, ShareRepositoryInterface
from app.modules.sharing.domain.models import ShareModel, ShareRecipientModel


class CreateShareUseCase:
    def __init__(
        self,
        share_repo: ShareRepositoryInterface,
        recipient_repo: ShareRecipientRepositoryInterface,
    ):
        self.share_repo = share_repo
        self.recipient_repo = recipient_repo

    async def execute(
        self,
        item_type: str,
        item_id: str,
        owner_id: str,
        visibility: str = "private",
        user_ids: list[str] | None = None,
        team_ids: list[str] | None = None,
        department_ids: list[str] | None = None,
        permission: str = "read",
    ) -> dict:
        if not item_type or not item_type.strip():
            raise ValidationException("Item type is required")

        valid_types = (
            "image", "entity", "paper", "project", "accession",
            "report", "notebook_entry", "sample", "team", "germplasm",
            "experiment",
        )
        if item_type not in valid_types:
            raise ValidationException(f"Invalid item type. Must be one of: {', '.join(valid_types)}")

        valid_visibilities = ("private", "link", "public")
        if visibility not in valid_visibilities:
            raise ValidationException(f"Invalid visibility. Must be one of: {', '.join(valid_visibilities)}")

        valid_permissions = ("read", "write")
        if permission not in valid_permissions:
            raise ValidationException(f"Invalid permission. Must be one of: {', '.join(valid_permissions)}")

        share_token = None
        if visibility == "link":
            share_token = _uuid.uuid4().hex[:24]

        share = ShareModel(
            id=_uuid.uuid4(),
            item_type=item_type.strip(),
            item_id=str(item_id).strip(),
            owner_id=_uuid.UUID(owner_id) if not isinstance(owner_id, _uuid.UUID) else owner_id,
            visibility=visibility,
            share_token=share_token,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        share = await self.share_repo.create(share)

        recipients = []
        recipient_models = []
        now = datetime.now(UTC)

        if user_ids:
            for uid in user_ids:
                parsed = _uuid.UUID(uid) if not isinstance(uid, _uuid.UUID) else uid
                recipient_models.append(
                    ShareRecipientModel(
                        id=_uuid.uuid4(),
                        share_id=share.id,
                        recipient_type="user",
                        user_id=parsed,
                        permission=permission,
                        shared_at=now,
                    )
                )

        if team_ids:
            for tid in team_ids:
                parsed = _uuid.UUID(tid) if not isinstance(tid, _uuid.UUID) else tid
                recipient_models.append(
                    ShareRecipientModel(
                        id=_uuid.uuid4(),
                        share_id=share.id,
                        recipient_type="team",
                        team_id=parsed,
                        permission=permission,
                        shared_at=now,
                    )
                )

        if department_ids:
            for did in department_ids:
                parsed = _uuid.UUID(did) if not isinstance(did, _uuid.UUID) else did
                recipient_models.append(
                    ShareRecipientModel(
                        id=_uuid.uuid4(),
                        share_id=share.id,
                        recipient_type="department",
                        department_id=parsed,
                        permission=permission,
                        shared_at=now,
                    )
                )

        if recipient_models:
            recipients = await self.recipient_repo.create_many(recipient_models)

        return {
            "share": share,
            "recipients": recipients,
        }


class ListSharedWithMeUseCase:
    def __init__(
        self,
        share_repo: ShareRepositoryInterface,
        recipient_repo: ShareRecipientRepositoryInterface,
    ):
        self.share_repo = share_repo
        self.recipient_repo = recipient_repo

    async def execute(self, user_id: str) -> list[dict]:
        memberships = await self.recipient_repo.list_user_memberships(user_id)
        recipients = await self.recipient_repo.list_shared_with_user(
            user_id,
            team_ids=memberships["team_ids"],
            department_ids=memberships["department_ids"],
        )

        results = []
        for recipient in recipients:
            share = await self.share_repo.get_by_id(str(recipient.share_id))
            if share:
                results.append({
                    "share": share,
                    "recipient": recipient,
                })

        return results


class ListMySharesUseCase:
    def __init__(
        self,
        share_repo: ShareRepositoryInterface,
        recipient_repo: ShareRecipientRepositoryInterface,
    ):
        self.share_repo = share_repo
        self.recipient_repo = recipient_repo

    async def execute(self, owner_id: str) -> list[dict]:
        shares = await self.share_repo.list_my_shares(owner_id)

        results = []
        for share in shares:
            recipients = await self.recipient_repo.list_by_share(str(share.id))
            results.append({
                "share": share,
                "recipients": recipients,
            })

        return results


class RevokeShareUseCase:
    def __init__(
        self,
        share_repo: ShareRepositoryInterface,
        recipient_repo: ShareRecipientRepositoryInterface,
    ):
        self.share_repo = share_repo
        self.recipient_repo = recipient_repo

    async def execute(self, share_id: str, user_id: str) -> bool:
        share = await self.share_repo.get_by_id(share_id)
        if not share:
            raise NotFoundException("Share", share_id)

        if str(share.owner_id) != user_id:
            raise ValidationException("Only the owner can revoke this share")

        await self.recipient_repo.delete_by_share(share_id)
        return await self.share_repo.delete(share_id)


class AccessByTokenUseCase:
    def __init__(self, share_repo: ShareRepositoryInterface):
        self.share_repo = share_repo

    async def execute(self, share_token: str) -> dict:
        share = await self.share_repo.get_by_token(share_token)
        if not share:
            raise NotFoundException("Share link")

        if share.visibility != "link":
            raise ValidationException("This share link is not valid for link access")

        return {
            "id": str(share.id),
            "item_type": share.item_type,
            "item_id": str(share.item_id),
            "permission": "read",
            "visibility": share.visibility,
            "created_at": share.created_at.isoformat(),
        }
