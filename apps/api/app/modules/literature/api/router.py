from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.modules.literature.api.schemas import (
    AddPaperToCollectionRequest,
    CollectionResponse,
    CreateCollectionRequest,
    CreateNoteRequest,
    CreatePaperRequest,
    NoteResponse,
    PaginatedCollectionsResponse,
    PaginatedNotesResponse,
    PaginatedPapersResponse,
    PaperResponse,
    SemanticSearchRequest,
    UpdateCollectionRequest,
    UpdateNoteRequest,
    UpdatePaperRequest,
)
from app.modules.literature.domain.use_cases import (
    AddPaperToCollectionUseCase,
    CreateCollectionUseCase,
    CreateNoteUseCase,
    CreatePaperUseCase,
    DeleteCollectionUseCase,
    DeleteNoteUseCase,
    DeletePaperUseCase,
    GetCollectionUseCase,
    GetNoteUseCase,
    GetPaperUseCase,
    ListCollectionsUseCase,
    ListNotesByPaperUseCase,
    ListPapersInCollectionUseCase,
    ListPapersUseCase,
    RemovePaperFromCollectionUseCase,
    SearchPapersSemanticUseCase,
    UpdateCollectionUseCase,
    UpdateNoteUseCase,
    UpdatePaperUseCase,
)

router = APIRouter()


# ────────────────────────── Papers ─────────────────────────────────────
@router.post("/papers", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def create_paper(
    request: CreatePaperRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.paper_repository import PaperRepository
    repo = PaperRepository(db)
    uc = CreatePaperUseCase(paper_repo=repo)
    return await uc.execute(
        title=request.title,
        user_id=current_user["id"],
        abstract=request.abstract,
        authors=request.authors,
        doi=request.doi,
        pmid=request.pmid,
        journal=request.journal,
        publication_date=request.publication_date,
        source=request.source,
        paper_type=request.paper_type,
        tags=request.tags,
        project_id=request.project_id,
    )


@router.get("/papers", response_model=PaginatedPapersResponse)
async def list_papers(
    skip: int = 0,
    limit: int = 20,
    project_id: str | None = None,
    source: str | None = None,
    paper_type: str | None = None,
    year: int | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.paper_repository import PaperRepository
    repo = PaperRepository(db)
    uc = ListPapersUseCase(paper_repo=repo)
    result = await uc.execute(
        skip=skip,
        limit=limit,
        project_id=project_id,
        source=source,
        paper_type=paper_type,
        year=year,
        search=search,
        user_id=current_user["id"],
    )
    return PaginatedPapersResponse(**result)


@router.get("/papers/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.paper_repository import PaperRepository
    repo = PaperRepository(db)
    uc = GetPaperUseCase(paper_repo=repo)
    return await uc.execute(paper_id)


@router.put("/papers/{paper_id}", response_model=PaperResponse)
async def update_paper(
    paper_id: str,
    request: UpdatePaperRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.paper_repository import PaperRepository
    repo = PaperRepository(db)
    uc = UpdatePaperUseCase(paper_repo=repo)
    return await uc.execute(
        paper_id=paper_id,
        user_id=current_user["id"],
        title=request.title,
        abstract=request.abstract,
        authors=request.authors,
        doi=request.doi,
        journal=request.journal,
        publication_date=request.publication_date,
        paper_type=request.paper_type,
        tags=request.tags,
        summary=request.summary,
    )


@router.delete("/papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.paper_repository import PaperRepository
    repo = PaperRepository(db)
    uc = DeletePaperUseCase(paper_repo=repo)
    await uc.execute(paper_id=paper_id, user_id=current_user["id"])


# ────────────────────────── Semantic Search ────────────────────────────
@router.post("/search", response_model=PaginatedPapersResponse)
async def search_papers_semantic(
    request: SemanticSearchRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.paper_repository import PaperRepository
    repo = PaperRepository(db)
    uc = SearchPapersSemanticUseCase(paper_repo=repo)
    embedding = [0.0] * 384
    papers = await uc.execute(
        query_embedding=embedding,
        limit=request.limit,
        project_id=request.project_id,
    )
    return PaginatedPapersResponse(
        items=[PaperResponse.model_validate(p) for p in papers],
        total=len(papers),
        skip=0,
        limit=request.limit,
    )


# ────────────────────────── Collections ────────────────────────────────
@router.post("/collections", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    request: CreateCollectionRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.collection_repository import CollectionRepository
    repo = CollectionRepository(db)
    uc = CreateCollectionUseCase(collection_repo=repo)
    return await uc.execute(
        name=request.name,
        user_id=current_user["id"],
        description=request.description,
        color=request.color,
        project_id=request.project_id,
        tags=request.tags,
    )


@router.get("/collections", response_model=PaginatedCollectionsResponse)
async def list_collections(
    skip: int = 0,
    limit: int = 20,
    project_id: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.collection_repository import CollectionRepository
    repo = CollectionRepository(db)
    uc = ListCollectionsUseCase(collection_repo=repo)
    result = await uc.execute(
        skip=skip,
        limit=limit,
        project_id=project_id,
        search=search,
        user_id=current_user["id"],
    )
    return PaginatedCollectionsResponse(**result)


@router.get("/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.collection_repository import CollectionRepository
    repo = CollectionRepository(db)
    uc = GetCollectionUseCase(collection_repo=repo)
    return await uc.execute(collection_id)


@router.put("/collections/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: str,
    request: UpdateCollectionRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.collection_repository import CollectionRepository
    repo = CollectionRepository(db)
    uc = UpdateCollectionUseCase(collection_repo=repo)
    return await uc.execute(
        collection_id=collection_id,
        user_id=current_user["id"],
        name=request.name,
        description=request.description,
        color=request.color,
        tags=request.tags,
    )


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.collection_repository import CollectionRepository
    repo = CollectionRepository(db)
    uc = DeleteCollectionUseCase(collection_repo=repo)
    await uc.execute(collection_id=collection_id, user_id=current_user["id"])


@router.post("/collections/{collection_id}/papers", status_code=status.HTTP_201_CREATED)
async def add_paper_to_collection(
    collection_id: str,
    request: AddPaperToCollectionRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.collection_repository import CollectionRepository
    from app.modules.literature.infrastructure.paper_repository import PaperRepository
    collection_repo = CollectionRepository(db)
    paper_repo = PaperRepository(db)
    uc = AddPaperToCollectionUseCase(collection_repo=collection_repo, paper_repo=paper_repo)
    await uc.execute(collection_id=collection_id, paper_id=request.paper_id)
    return {"message": "Paper added to collection"}


@router.delete("/collections/{collection_id}/papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_paper_from_collection(
    collection_id: str,
    paper_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.collection_repository import CollectionRepository
    repo = CollectionRepository(db)
    uc = RemovePaperFromCollectionUseCase(collection_repo=repo)
    await uc.execute(collection_id=collection_id, paper_id=paper_id)


@router.get("/collections/{collection_id}/papers", response_model=PaginatedPapersResponse)
async def list_papers_in_collection(
    collection_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.collection_repository import CollectionRepository
    repo = CollectionRepository(db)
    uc = ListPapersInCollectionUseCase(collection_repo=repo)
    result = await uc.execute(collection_id=collection_id, skip=skip, limit=limit)
    return PaginatedPapersResponse(**result)


# ────────────────────────── Notes ──────────────────────────────────────
@router.post("/papers/{paper_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    paper_id: str,
    request: CreateNoteRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.note_repository import NoteRepository
    from app.modules.literature.infrastructure.paper_repository import PaperRepository
    note_repo = NoteRepository(db)
    paper_repo = PaperRepository(db)
    uc = CreateNoteUseCase(note_repo=note_repo, paper_repo=paper_repo)
    return await uc.execute(
        paper_id=paper_id,
        content=request.content,
        user_id=current_user["id"],
        page_number=request.page_number,
        highlight_text=request.highlight_text,
        tags=request.tags,
    )


@router.get("/papers/{paper_id}/notes", response_model=PaginatedNotesResponse)
async def list_notes(
    paper_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.note_repository import NoteRepository
    repo = NoteRepository(db)
    uc = ListNotesByPaperUseCase(note_repo=repo)
    result = await uc.execute(paper_id=paper_id, skip=skip, limit=limit)
    return PaginatedNotesResponse(**result)


@router.get("/papers/{paper_id}/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    paper_id: str,
    note_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.note_repository import NoteRepository
    repo = NoteRepository(db)
    uc = GetNoteUseCase(note_repo=repo)
    return await uc.execute(note_id)


@router.put("/papers/{paper_id}/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    paper_id: str,
    note_id: str,
    request: UpdateNoteRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.note_repository import NoteRepository
    repo = NoteRepository(db)
    uc = UpdateNoteUseCase(note_repo=repo)
    return await uc.execute(
        note_id=note_id,
        user_id=current_user["id"],
        content=request.content,
        page_number=request.page_number,
        highlight_text=request.highlight_text,
        tags=request.tags,
    )


@router.delete("/papers/{paper_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    paper_id: str,
    note_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.literature.infrastructure.note_repository import NoteRepository
    repo = NoteRepository(db)
    uc = DeleteNoteUseCase(note_repo=repo)
    await uc.execute(note_id=note_id, user_id=current_user["id"])
