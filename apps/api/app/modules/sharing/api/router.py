from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
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


def _recipient_to_dict(recipient) -> dict:
    return {
        "id": str(recipient.id),
        "user_id": str(recipient.user_id),
        "permission": recipient.permission,
        "shared_at": recipient.shared_at.isoformat(),
    }


@router.post("/share", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
async def share_item(
    request: CreateShareRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.sharing.infrastructure.repositories import ShareRecipientRepository, ShareRepository

    share_repo = ShareRepository(db)
    recipient_repo = ShareRecipientRepository(db)
    uc = CreateShareUseCase(share_repo=share_repo, recipient_repo=recipient_repo)
    result = await uc.execute(
        item_type=request.item_type,
        item_id=request.item_id,
        owner_id=current_user["id"],
        visibility=request.visibility,
        user_ids=request.user_ids,
        permission=request.permission,
    )
    share_dict = _share_to_dict(result["share"])
    share_dict["recipients"] = [_recipient_to_dict(r) for r in result["recipients"]]
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
    return [
        {
            "share": _share_to_dict(item["share"]),
            "recipient": _recipient_to_dict(item["recipient"]),
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
    return [
        {
            "share": _share_to_dict(item["share"]),
            "recipients": [_recipient_to_dict(r) for r in item["recipients"]],
        }
        for item in results
    ]


@router.delete("/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_share(
    share_id: str,
    current_user=Depends(get_current_active_user),
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
