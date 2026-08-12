from pydantic import BaseModel, Field

from app.core.serializers import OrmSerializableMixin


class CreateShareRequest(BaseModel):
    item_type: str = Field(
        ...,
        pattern="^(image|entity|paper|project|accession|report|notebook_entry|sample|team|germplasm|experiment)$",
    )
    item_id: str
    visibility: str = Field(
        "private",
        pattern="^(private|link|public)$",
    )
    user_ids: list[str] | None = Field(None, max_length=100)
    emails: list[str] | None = Field(None, max_length=100)
    team_ids: list[str] | None = Field(None, max_length=100)
    department_ids: list[str] | None = Field(None, max_length=100)
    permission: str = Field(
        "read",
        pattern="^(read|write)$",
    )


class ShareRecipientResponse(OrmSerializableMixin):
    id: str
    recipient_type: str
    user_id: str | None = None
    team_id: str | None = None
    department_id: str | None = None
    permission: str
    shared_at: str
    user: dict | None = None


class ShareResponse(OrmSerializableMixin):
    id: str
    item_type: str
    item_id: str
    owner_id: str
    visibility: str
    share_token: str | None = None
    created_at: str
    updated_at: str
    recipients: list[ShareRecipientResponse] = []


class SharedWithMeItemResponse(OrmSerializableMixin):
    share: ShareResponse
    recipient: ShareRecipientResponse


class MyShareItemResponse(OrmSerializableMixin):
    share: ShareResponse
    recipients: list[ShareRecipientResponse]


class ShareLinkAccessResponse(OrmSerializableMixin):
    id: str
    item_type: str
    item_id: str
    permission: str
    visibility: str
    created_at: str
