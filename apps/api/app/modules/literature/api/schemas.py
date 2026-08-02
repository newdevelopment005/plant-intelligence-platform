from datetime import date

from pydantic import BaseModel, Field


class CreatePaperRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=1000)
    abstract: str | None = Field(None, max_length=50000)
    authors: list[str] | None = Field(None, max_length=100)
    doi: str | None = Field(None, max_length=255)
    pmid: str | None = Field(None, max_length=50)
    journal: str | None = Field(None, max_length=500)
    publication_date: date | None = None
    source: str = Field(
        "manual",
        pattern="^(manual|pubmed|crossref|arxiv|biorxiv|doaj|import)$",
    )
    paper_type: str = Field(
        "article",
        pattern="^(article|review|meta_analysis|systematic_review|preprint|book_chapter|conference_paper|thesis|other)$",
    )
    tags: list[str] | None = Field(None, max_length=20)
    project_id: str | None = None


class UpdatePaperRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=1000)
    abstract: str | None = Field(None, max_length=50000)
    authors: list[str] | None = Field(None, max_length=100)
    doi: str | None = Field(None, max_length=255)
    journal: str | None = Field(None, max_length=500)
    publication_date: date | None = None
    paper_type: str | None = Field(
        None,
        pattern="^(article|review|meta_analysis|systematic_review|preprint|book_chapter|conference_paper|thesis|other)$",
    )
    tags: list[str] | None = Field(None, max_length=20)
    summary: str | None = Field(None, max_length=10000)


class PaperResponse(BaseModel):
    id: str
    title: str
    abstract: str | None = None
    authors: list[str] | None = None
    doi: str | None = None
    pmid: str | None = None
    journal: str | None = None
    publication_date: str | None = None
    year: int | None = None
    source: str
    paper_type: str
    tags: list[str] | None = None
    project_id: str | None = None
    citations_count: int | None = None
    summary: str | None = None
    is_open_access: bool = False
    created_by: str
    created_at: str
    updated_at: str


class PaginatedPapersResponse(BaseModel):
    items: list[PaperResponse]
    total: int
    skip: int
    limit: int


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(10, ge=1, le=100)
    project_id: str | None = None


class CreateCollectionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    color: str | None = Field(None, max_length=7)
    project_id: str | None = None
    tags: list[str] | None = Field(None, max_length=20)


class UpdateCollectionRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    color: str | None = Field(None, max_length=7)
    tags: list[str] | None = Field(None, max_length=20)


class CollectionResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    color: str | None = None
    project_id: str | None = None
    tags: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedCollectionsResponse(BaseModel):
    items: list[CollectionResponse]
    total: int
    skip: int
    limit: int


class AddPaperToCollectionRequest(BaseModel):
    paper_id: str


class CreateNoteRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    page_number: int | None = Field(None, ge=0)
    highlight_text: str | None = Field(None, max_length=5000)
    tags: list[str] | None = Field(None, max_length=20)


class UpdateNoteRequest(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=10000)
    page_number: int | None = Field(None, ge=0)
    highlight_text: str | None = Field(None, max_length=5000)
    tags: list[str] | None = Field(None, max_length=20)


class NoteResponse(BaseModel):
    id: str
    paper_id: str
    content: str
    page_number: int | None = None
    highlight_text: str | None = None
    tags: list[str] | None = None
    created_by: str
    created_at: str
    updated_at: str


class PaginatedNotesResponse(BaseModel):
    items: list[NoteResponse]
    total: int
    skip: int
    limit: int
