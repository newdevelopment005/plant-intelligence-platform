from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, require_not_readonly
from app.database import get_db
from app.modules.sharing.api.schemas import (
    CreateShareRequest,
    MyShareItemResponse,
    ShareLinkAccessResponse,
    ShareRecipientResponse,
    ShareResponse,
    SharedWithMeItemResponse,
)
from app.modules.sharing.domain.use_cases import (
    AccessByTokenUseCase,
    CreateShareUseCase,
    ListMySharesUseCase,
    ListSharedWithMeUseCase,
    RevokeShareUseCase,
)

router = APIRouter(redirect_slashes=False)


def _share_to_dict(share) -> dict:
    return {
        "id": str(share.id),
        "item_type": share.item_type,
        "item_id": str(share.item_id),
        "owner_id": str(share.owner_id),
        "visibility": share.visibility,
        "share_token": share.share_token,
        "created_at": share.created_at.isoformat(),
        "updated_at": share.updated_at.isoformat(),
    }


def _recipient_to_dict(recipient, user: dict | None = None) -> dict:
    result = {
        "id": str(recipient.id),
        "recipient_type": recipient.recipient_type,
        "user_id": str(recipient.user_id) if recipient.user_id else None,
        "team_id": str(recipient.team_id) if recipient.team_id else None,
        "department_id": str(recipient.department_id) if recipient.department_id else None,
        "permission": recipient.permission,
        "shared_at": recipient.shared_at.isoformat(),
    }
    if user:
        result["user"] = {
            "id": str(user.get("id") or user.get("user_id")),
            "full_name": user.get("full_name"),
            "email": user.get("email"),
        }
    return result


async def _users_by_ids(db: AsyncSession, user_ids: list[str]) -> dict:
    from app.modules.auth.infrastructure.repositories import UserRepository

    users = await UserRepository(db).get_by_ids(user_ids)
    return {str(u.id): {"id": str(u.id), "full_name": u.full_name, "email": u.email} for u in users}


def _attach_owner(share_dict: dict, owners: dict) -> dict:
    owner = owners.get(share_dict.get("owner_id"))
    if owner:
        share_dict["owner"] = owner
    return share_dict


async def _resolve_emails_to_user_ids(db: AsyncSession, emails: list[str] | None) -> list[str]:
    from app.modules.auth.infrastructure.repositories import UserRepository

    if not emails:
        return []
    user_repo = UserRepository(db)
    resolved = []
    for email in emails:
        user = await user_repo.get_by_email(email)
        if user:
            resolved.append(str(user.id))
    return resolved


@router.post("/share", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
async def share_item(
    request: CreateShareRequest,
    current_user=Depends(require_not_readonly),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.sharing.infrastructure.repositories import ShareRecipientRepository, ShareRepository

    share_repo = ShareRepository(db)
    recipient_repo = ShareRecipientRepository(db)
    uc = CreateShareUseCase(share_repo=share_repo, recipient_repo=recipient_repo)

    all_user_ids = list(request.user_ids or [])
    emails = list(request.emails or [])
    email_ids = await _resolve_emails_to_user_ids(db, emails)
    all_user_ids.extend(email_ids)
    all_user_ids = list(dict.fromkeys(all_user_ids))

    result = await uc.execute(
        item_type=request.item_type,
        item_id=request.item_id,
        owner_id=current_user["id"],
        visibility=request.visibility,
        user_ids=all_user_ids,
        team_ids=request.team_ids,
        department_ids=request.department_ids,
        permission=request.permission,
    )
    share_dict = _share_to_dict(result["share"])
    recipient_ids = [str(r.user_id) for r in result["recipients"] if r.user_id]
    users = await _users_by_ids(db, recipient_ids)
    share_dict["recipients"] = [
        _recipient_to_dict(r, users.get(str(r.user_id)) if r.user_id else None)
        for r in result["recipients"]
    ]

    for r in result["recipients"]:
        user = users.get(str(r.user_id))
        if user and user.get("email") and user.get("email") != current_user.get("email"):
            from app.core.email import send_share_notification

            send_share_notification(
                to_email=user["email"],
                sharer_name=current_user.get("full_name") or current_user.get("email") or "A colleague",
                item_type=share_dict["item_type"],
                item_id=share_dict["item_id"],
                permission=share_dict["recipients"][0]["permission"],
                base_url="https://plant-intelligence-platform.vercel.app",
            )

    if emails:
        resolved_set = set(email_ids)
        unresolved = [e for e in emails if e not in resolved_set]
        if unresolved:
            from app.core.email import send_share_invite_to_unresolved

            for email in unresolved:
                send_share_invite_to_unresolved(
                    to_email=email,
                    sharer_name=current_user.get("full_name") or current_user.get("email") or "A colleague",
                    item_type=share_dict["item_type"],
                    base_url="https://plant-intelligence-platform.vercel.app",
                )
            share_dict["unresolved_emails"] = unresolved
    return share_dict


@router.get("/shared-with-me")
async def list_shared_with_me(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.sharing.infrastructure.repositories import ShareRecipientRepository, ShareRepository

    share_repo = ShareRepository(db)
    recipient_repo = ShareRecipientRepository(db)
    uc = ListSharedWithMeUseCase(share_repo=share_repo, recipient_repo=recipient_repo)
    results = await uc.execute(user_id=current_user["id"])
    user_ids = [str(item["recipient"].user_id) for item in results if item["recipient"].user_id]
    users = await _users_by_ids(db, user_ids)
    owner_ids = [str(item["share"].owner_id) for item in results]
    owners = await _users_by_ids(db, owner_ids)
    return [
        {
            "share": _attach_owner(_share_to_dict(item["share"]), owners),
            "recipient": _recipient_to_dict(
                item["recipient"],
                users.get(str(item["recipient"].user_id)) if item["recipient"].user_id else None,
            ),
        }
        for item in results
    ]


@router.get("/my-shares")
async def list_my_shares(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.sharing.infrastructure.repositories import ShareRecipientRepository, ShareRepository

    share_repo = ShareRepository(db)
    recipient_repo = ShareRecipientRepository(db)
    uc = ListMySharesUseCase(share_repo=share_repo, recipient_repo=recipient_repo)
    results = await uc.execute(owner_id=current_user["id"])
    serialized = []
    for item in results:
        recipient_ids = [str(r.user_id) for r in item["recipients"] if r.user_id]
        users = await _users_by_ids(db, recipient_ids)
        owners = await _users_by_ids(db, [str(item["share"].owner_id)])
        serialized.append(
            {
                "share": _attach_owner(_share_to_dict(item["share"]), owners),
                "recipients": [
                    _recipient_to_dict(r, users.get(str(r.user_id)) if r.user_id else None)
                    for r in item["recipients"]
                ],
            }
        )
    return serialized


@router.delete("/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_share(
    share_id: str,
    current_user=Depends(require_not_readonly),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.sharing.infrastructure.repositories import ShareRecipientRepository, ShareRepository

    share_repo = ShareRepository(db)
    recipient_repo = ShareRecipientRepository(db)
    uc = RevokeShareUseCase(share_repo=share_repo, recipient_repo=recipient_repo)
    await uc.execute(share_id=share_id, user_id=current_user["id"])


@router.get("/access/{token}", response_model=ShareLinkAccessResponse)
async def access_by_token(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    from app.modules.sharing.infrastructure.repositories import ShareRepository

    share_repo = ShareRepository(db)
    uc = AccessByTokenUseCase(share_repo=share_repo)
    return await uc.execute(share_token=token)
