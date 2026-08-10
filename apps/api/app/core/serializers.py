from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


def coerce_str(value):
    """Convert ORM-native values (UUID/datetime/date) to serializable strings.

    Non-matching values are passed through untouched so it is safe to apply
    to every field in a response schema.
    """
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


class OrmSerializableMixin(BaseModel):
    """Coerces ORM-native UUID/date/datetime values into strings for any field.

    Inherit from this instead of BaseModel for response schemas that are
    populated directly from SQLAlchemy models.
    """

    @field_validator("*", mode="before")
    @classmethod
    def _coerce_orm_values(cls, value):
        return coerce_str(value)