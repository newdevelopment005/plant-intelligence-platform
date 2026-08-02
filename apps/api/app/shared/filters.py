from enum import StrEnum

from pydantic import BaseModel, Field


class SortOrder(StrEnum):
    asc = "asc"
    desc = "desc"


class BaseFilter(BaseModel):
    search: str | None = None
    sort_by: str | None = None
    sort_order: SortOrder = SortOrder.desc
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
