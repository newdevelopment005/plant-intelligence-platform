from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.core.serializers import OrmSerializableMixin


class CreateMeetingRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = Field(None, max_length=5000)
    starts_at: datetime
    ends_at: datetime | None = None
    location: str | None = Field(None, max_length=255)
    meeting_link: str | None = Field(None, max_length=500)
    reminder_option: str | None = Field(
        None, pattern="^(at_time|5m|10m|15m|30m|1h|1d)$"
    )
    attendee_emails: list[EmailStr] | None = Field(None, max_length=100)


class UpdateMeetingRequest(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = Field(None, max_length=5000)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    location: str | None = Field(None, max_length=255)
    meeting_link: str | None = Field(None, max_length=500)
    reminder_option: str | None = Field(
        None, pattern="^(at_time|5m|10m|15m|30m|1h|1d)$"
    )


class UpdateAttendeeStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(accepted|declined)$")


class AttendeeResponse(OrmSerializableMixin):
    id: str
    user_id: str | None = None
    email: str | None = None
    status: str
    invited_at: str


class MeetingResponse(OrmSerializableMixin):
    id: str
    title: str
    description: str | None = None
    starts_at: str
    ends_at: str | None = None
    location: str | None = None
    meeting_link: str | None = None
    reminder_minutes_before: int
    created_by: str
    created_at: str
    updated_at: str
    attendees: list[AttendeeResponse] = []


class MeetingListItemResponse(OrmSerializableMixin):
    id: str
    title: str
    description: str | None = None
    starts_at: str
    ends_at: str | None = None
    location: str | None = None
    meeting_link: str | None = None
    reminder_minutes_before: int
    created_by: str
    created_at: str
    updated_at: str


class PaginatedMeetingsResponse(BaseModel):
    items: list[MeetingListItemResponse]
    total: int
    skip: int
    limit: int