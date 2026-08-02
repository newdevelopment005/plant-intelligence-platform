from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    cursor: str | None = None
    limit: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False
    total: int | None = None


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
