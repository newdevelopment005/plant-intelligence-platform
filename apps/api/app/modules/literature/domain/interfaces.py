from abc import ABC, abstractmethod

from app.modules.literature.domain.models import (
    CollectionModel,
    NoteModel,
    PaperModel,
)


class PaperRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, paper: PaperModel) -> PaperModel: ...

    @abstractmethod
    async def get_by_id(self, paper_id: str) -> PaperModel | None: ...

    @abstractmethod
    async def get_by_doi(self, doi: str) -> PaperModel | None: ...

    @abstractmethod
    async def get_by_pmid(self, pmid: str) -> PaperModel | None: ...

    @abstractmethod
    async def list_papers(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        source: str | None = None,
        paper_type: str | None = None,
        year: int | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[PaperModel]: ...

    @abstractmethod
    async def count_papers(
        self,
        project_id: str | None = None,
        source: str | None = None,
        paper_type: str | None = None,
        year: int | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def update(self, paper: PaperModel) -> PaperModel: ...

    @abstractmethod
    async def delete(self, paper_id: str) -> bool: ...

    @abstractmethod
    async def search_semantic(
        self, query_embedding: list[float], limit: int = 10, project_id: str | None = None
    ) -> list[PaperModel]: ...


class CollectionRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, collection: CollectionModel) -> CollectionModel: ...

    @abstractmethod
    async def get_by_id(self, collection_id: str) -> CollectionModel | None: ...

    @abstractmethod
    async def list_collections(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[CollectionModel]: ...

    @abstractmethod
    async def count_collections(
        self,
        project_id: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def update(self, collection: CollectionModel) -> CollectionModel: ...

    @abstractmethod
    async def delete(self, collection_id: str) -> bool: ...

    @abstractmethod
    async def add_paper(self, collection_id: str, paper_id: str) -> bool: ...

    @abstractmethod
    async def remove_paper(self, collection_id: str, paper_id: str) -> bool: ...

    @abstractmethod
    async def list_papers_in_collection(
        self, collection_id: str, skip: int = 0, limit: int = 100
    ) -> list[PaperModel]: ...

    @abstractmethod
    async def count_papers_in_collection(self, collection_id: str) -> int: ...

    @abstractmethod
    async def paper_in_collection(self, collection_id: str, paper_id: str) -> bool: ...


class NoteRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, note: NoteModel) -> NoteModel: ...

    @abstractmethod
    async def get_by_id(self, note_id: str) -> NoteModel | None: ...

    @abstractmethod
    async def list_by_paper(
        self, paper_id: str, skip: int = 0, limit: int = 100
    ) -> list[NoteModel]: ...

    @abstractmethod
    async def count_by_paper(self, paper_id: str) -> int: ...

    @abstractmethod
    async def update(self, note: NoteModel) -> NoteModel: ...

    @abstractmethod
    async def delete(self, note_id: str) -> bool: ...
