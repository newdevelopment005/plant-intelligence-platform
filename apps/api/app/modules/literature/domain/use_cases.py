from datetime import UTC, datetime

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.literature.domain.interfaces import (
    CollectionRepositoryInterface,
    NoteRepositoryInterface,
    PaperRepositoryInterface,
)
from app.modules.literature.domain.models import (
    CollectionModel,
    NoteModel,
    PaperModel,
)


class CreatePaperUseCase:
    def __init__(self, paper_repo: PaperRepositoryInterface):
        self.paper_repo = paper_repo

    async def execute(
        self,
        title: str,
        user_id: str,
        abstract: str | None = None,
        authors: list[str] | None = None,
        doi: str | None = None,
        pmid: str | None = None,
        journal: str | None = None,
        publication_date=None,
        source: str = "manual",
        paper_type: str = "article",
        tags: list[str] | None = None,
        project_id: str | None = None,
    ) -> PaperModel:
        if not title or not title.strip():
            raise ValidationException("Paper title is required")
        if len(title.strip()) > 1000:
            raise ValidationException("Paper title must be less than 1000 characters")

        if doi:
            existing = await self.paper_repo.get_by_doi(doi)
            if existing:
                raise ValidationException(f"Paper with DOI {doi} already exists")

        if pmid:
            existing = await self.paper_repo.get_by_pmid(pmid)
            if existing:
                raise ValidationException(f"Paper with PMID {pmid} already exists")

        valid_sources = ("manual", "pubmed", "crossref", "arxiv", "biorxiv", "doaj", "import")
        if source not in valid_sources:
            raise ValidationException(f"Invalid source. Must be one of: {', '.join(valid_sources)}")

        valid_types = ("article", "review", "meta_analysis", "systematic_review", "preprint", "book_chapter", "conference_paper", "thesis", "other")
        if paper_type not in valid_types:
            raise ValidationException(f"Invalid paper type. Must be one of: {', '.join(valid_types)}")

        year = publication_date.year if publication_date else None

        paper = PaperModel(
            title=title.strip(),
            abstract=abstract.strip() if abstract else None,
            authors=authors,
            doi=doi.strip() if doi else None,
            pmid=pmid.strip() if pmid else None,
            journal=journal.strip() if journal else None,
            publication_date=publication_date,
            year=year,
            source=source,
            paper_type=paper_type,
            tags=tags,
            project_id=project_id,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.paper_repo.create(paper)


class GetPaperUseCase:
    def __init__(self, paper_repo: PaperRepositoryInterface):
        self.paper_repo = paper_repo

    async def execute(self, paper_id: str) -> PaperModel:
        paper = await self.paper_repo.get_by_id(paper_id)
        if not paper:
            raise NotFoundException("Paper", paper_id)
        return paper


class ListPapersUseCase:
    def __init__(self, paper_repo: PaperRepositoryInterface):
        self.paper_repo = paper_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        source: str | None = None,
        paper_type: str | None = None,
        year: int | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        papers = await self.paper_repo.list_papers(
            skip=skip,
            limit=limit,
            project_id=project_id,
            source=source,
            paper_type=paper_type,
            year=year,
            search=search,
            user_id=user_id,
        )
        total = await self.paper_repo.count_papers(
            project_id=project_id,
            source=source,
            paper_type=paper_type,
            year=year,
            search=search,
            user_id=user_id,
        )

        return {
            "items": [
                {
                    "id": str(p.id),
                    "title": p.title,
                    "abstract": p.abstract,
                    "authors": p.authors,
                    "doi": p.doi,
                    "pmid": p.pmid,
                    "journal": p.journal,
                    "publication_date": p.publication_date.isoformat() if p.publication_date else None,
                    "year": p.year,
                    "source": p.source,
                    "paper_type": p.paper_type,
                    "tags": p.tags,
                    "project_id": str(p.project_id) if p.project_id else None,
                    "citations_count": p.citations_count,
                    "summary": p.summary,
                    "created_by": str(p.created_by),
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat(),
                }
                for p in papers
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdatePaperUseCase:
    def __init__(self, paper_repo: PaperRepositoryInterface):
        self.paper_repo = paper_repo

    async def execute(
        self,
        paper_id: str,
        user_id: str,
        title: str | None = None,
        abstract: str | None = None,
        authors: list[str] | None = None,
        doi: str | None = None,
        journal: str | None = None,
        publication_date=None,
        paper_type: str | None = None,
        tags: list[str] | None = None,
        summary: str | None = None,
    ) -> PaperModel:
        paper = await self.paper_repo.get_by_id(paper_id)
        if not paper:
            raise NotFoundException("Paper", paper_id)

        if str(paper.created_by) != user_id:
            raise ValidationException("Only the creator can update this paper")

        if title is not None:
            if not title.strip():
                raise ValidationException("Paper title cannot be empty")
            paper.title = title.strip()
        if abstract is not None:
            paper.abstract = abstract.strip() if abstract else None
        if authors is not None:
            paper.authors = authors
        if doi is not None:
            paper.doi = doi.strip() if doi else None
        if journal is not None:
            paper.journal = journal.strip() if journal else None
        if publication_date is not None:
            paper.publication_date = publication_date
            paper.year = publication_date.year if publication_date else None
        if paper_type is not None:
            valid_types = ("article", "review", "meta_analysis", "systematic_review", "preprint", "book_chapter", "conference_paper", "thesis", "other")
            if paper_type not in valid_types:
                raise ValidationException("Invalid paper type")
            paper.paper_type = paper_type
        if tags is not None:
            paper.tags = tags
        if summary is not None:
            paper.summary = summary.strip() if summary else None

        paper.updated_at = datetime.now(UTC)
        return await self.paper_repo.update(paper)


class DeletePaperUseCase:
    def __init__(self, paper_repo: PaperRepositoryInterface):
        self.paper_repo = paper_repo

    async def execute(self, paper_id: str, user_id: str) -> bool:
        paper = await self.paper_repo.get_by_id(paper_id)
        if not paper:
            raise NotFoundException("Paper", paper_id)

        if str(paper.created_by) != user_id:
            raise ValidationException("Only the creator can delete this paper")

        return await self.paper_repo.delete(paper_id)


class SearchPapersSemanticUseCase:
    def __init__(self, paper_repo: PaperRepositoryInterface):
        self.paper_repo = paper_repo

    async def execute(
        self,
        query_embedding: list[float],
        limit: int = 10,
        project_id: str | None = None,
    ) -> list[PaperModel]:
        if not query_embedding:
            raise ValidationException("Query embedding is required")
        return await self.paper_repo.search_semantic(
            query_embedding=query_embedding,
            limit=limit,
            project_id=project_id,
        )


class CreateCollectionUseCase:
    def __init__(self, collection_repo: CollectionRepositoryInterface):
        self.collection_repo = collection_repo

    async def execute(
        self,
        name: str,
        user_id: str,
        description: str | None = None,
        color: str | None = None,
        project_id: str | None = None,
        tags: list[str] | None = None,
    ) -> CollectionModel:
        if not name or not name.strip():
            raise ValidationException("Collection name is required")
        if len(name.strip()) > 255:
            raise ValidationException("Collection name must be less than 255 characters")

        collection = CollectionModel(
            name=name.strip(),
            description=description.strip() if description else None,
            color=color,
            project_id=project_id,
            tags=tags,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.collection_repo.create(collection)


class GetCollectionUseCase:
    def __init__(self, collection_repo: CollectionRepositoryInterface):
        self.collection_repo = collection_repo

    async def execute(self, collection_id: str) -> CollectionModel:
        collection = await self.collection_repo.get_by_id(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)
        return collection


class ListCollectionsUseCase:
    def __init__(self, collection_repo: CollectionRepositoryInterface):
        self.collection_repo = collection_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        collections = await self.collection_repo.list_collections(
            skip=skip, limit=limit, project_id=project_id, search=search, user_id=user_id
        )
        total = await self.collection_repo.count_collections(
            project_id=project_id, search=search, user_id=user_id
        )
        return {
            "items": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "description": c.description,
                    "color": c.color,
                    "project_id": str(c.project_id) if c.project_id else None,
                    "tags": c.tags,
                    "created_by": str(c.created_by),
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                }
                for c in collections
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateCollectionUseCase:
    def __init__(self, collection_repo: CollectionRepositoryInterface):
        self.collection_repo = collection_repo

    async def execute(
        self,
        collection_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
        tags: list[str] | None = None,
    ) -> CollectionModel:
        collection = await self.collection_repo.get_by_id(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)

        if str(collection.created_by) != user_id:
            raise ValidationException("Only the creator can update this collection")

        if name is not None:
            if not name.strip():
                raise ValidationException("Collection name cannot be empty")
            collection.name = name.strip()
        if description is not None:
            collection.description = description.strip() if description else None
        if color is not None:
            collection.color = color
        if tags is not None:
            collection.tags = tags

        collection.updated_at = datetime.now(UTC)
        return await self.collection_repo.update(collection)


class DeleteCollectionUseCase:
    def __init__(self, collection_repo: CollectionRepositoryInterface):
        self.collection_repo = collection_repo

    async def execute(self, collection_id: str, user_id: str) -> bool:
        collection = await self.collection_repo.get_by_id(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)

        if str(collection.created_by) != user_id:
            raise ValidationException("Only the creator can delete this collection")

        return await self.collection_repo.delete(collection_id)


class AddPaperToCollectionUseCase:
    def __init__(self, collection_repo: CollectionRepositoryInterface, paper_repo: PaperRepositoryInterface):
        self.collection_repo = collection_repo
        self.paper_repo = paper_repo

    async def execute(self, collection_id: str, paper_id: str) -> bool:
        collection = await self.collection_repo.get_by_id(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)

        paper = await self.paper_repo.get_by_id(paper_id)
        if not paper:
            raise NotFoundException("Paper", paper_id)

        already_in = await self.collection_repo.paper_in_collection(collection_id, paper_id)
        if already_in:
            raise ValidationException("Paper is already in this collection")

        return await self.collection_repo.add_paper(collection_id, paper_id)


class RemovePaperFromCollectionUseCase:
    def __init__(self, collection_repo: CollectionRepositoryInterface):
        self.collection_repo = collection_repo

    async def execute(self, collection_id: str, paper_id: str) -> bool:
        collection = await self.collection_repo.get_by_id(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)

        return await self.collection_repo.remove_paper(collection_id, paper_id)


class ListPapersInCollectionUseCase:
    def __init__(self, collection_repo: CollectionRepositoryInterface):
        self.collection_repo = collection_repo

    async def execute(
        self, collection_id: str, skip: int = 0, limit: int = 100
    ) -> dict:
        collection = await self.collection_repo.get_by_id(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)

        papers = await self.collection_repo.list_papers_in_collection(
            collection_id, skip=skip, limit=limit
        )
        total = await self.collection_repo.count_papers_in_collection(collection_id)

        return {
            "items": [
                {
                    "id": str(p.id),
                    "title": p.title,
                    "authors": p.authors,
                    "doi": p.doi,
                    "journal": p.journal,
                    "year": p.year,
                    "source": p.source,
                    "created_at": p.created_at.isoformat(),
                }
                for p in papers
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class CreateNoteUseCase:
    def __init__(self, note_repo: NoteRepositoryInterface, paper_repo: PaperRepositoryInterface):
        self.note_repo = note_repo
        self.paper_repo = paper_repo

    async def execute(
        self,
        paper_id: str,
        content: str,
        user_id: str,
        page_number: int | None = None,
        highlight_text: str | None = None,
        tags: list[str] | None = None,
    ) -> NoteModel:
        paper = await self.paper_repo.get_by_id(paper_id)
        if not paper:
            raise NotFoundException("Paper", paper_id)

        if not content or not content.strip():
            raise ValidationException("Note content is required")

        note = NoteModel(
            paper_id=paper_id,
            content=content.strip(),
            page_number=page_number,
            highlight_text=highlight_text.strip() if highlight_text else None,
            tags=tags,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.note_repo.create(note)


class GetNoteUseCase:
    def __init__(self, note_repo: NoteRepositoryInterface):
        self.note_repo = note_repo

    async def execute(self, note_id: str) -> NoteModel:
        note = await self.note_repo.get_by_id(note_id)
        if not note:
            raise NotFoundException("Note", note_id)
        return note


class ListNotesByPaperUseCase:
    def __init__(self, note_repo: NoteRepositoryInterface):
        self.note_repo = note_repo

    async def execute(
        self, paper_id: str, skip: int = 0, limit: int = 100
    ) -> dict:
        notes = await self.note_repo.list_by_paper(paper_id, skip=skip, limit=limit)
        total = await self.note_repo.count_by_paper(paper_id)
        return {
            "items": [
                {
                    "id": str(n.id),
                    "paper_id": str(n.paper_id),
                    "content": n.content,
                    "page_number": n.page_number,
                    "highlight_text": n.highlight_text,
                    "tags": n.tags,
                    "created_by": str(n.created_by),
                    "created_at": n.created_at.isoformat(),
                    "updated_at": n.updated_at.isoformat(),
                }
                for n in notes
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateNoteUseCase:
    def __init__(self, note_repo: NoteRepositoryInterface):
        self.note_repo = note_repo

    async def execute(
        self,
        note_id: str,
        user_id: str,
        content: str | None = None,
        page_number: int | None = None,
        highlight_text: str | None = None,
        tags: list[str] | None = None,
    ) -> NoteModel:
        note = await self.note_repo.get_by_id(note_id)
        if not note:
            raise NotFoundException("Note", note_id)

        if str(note.created_by) != user_id:
            raise ValidationException("Only the creator can update this note")

        if content is not None:
            if not content.strip():
                raise ValidationException("Note content cannot be empty")
            note.content = content.strip()
        if page_number is not None:
            note.page_number = page_number
        if highlight_text is not None:
            note.highlight_text = highlight_text.strip() if highlight_text else None
        if tags is not None:
            note.tags = tags

        note.updated_at = datetime.now(UTC)
        return await self.note_repo.update(note)


class DeleteNoteUseCase:
    def __init__(self, note_repo: NoteRepositoryInterface):
        self.note_repo = note_repo

    async def execute(self, note_id: str, user_id: str) -> bool:
        note = await self.note_repo.get_by_id(note_id)
        if not note:
            raise NotFoundException("Note", note_id)

        if str(note.created_by) != user_id:
            raise ValidationException("Only the creator can delete this note")

        return await self.note_repo.delete(note_id)
