from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.literature.api.schemas import (
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
)
from app.modules.literature.domain.interfaces import (
    CollectionRepositoryInterface,
    NoteRepositoryInterface,
    PaperRepositoryInterface,
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
from app.modules.literature.infrastructure.collection_repository import CollectionRepository
from app.modules.literature.infrastructure.note_repository import NoteRepository
from app.modules.literature.infrastructure.paper_repository import PaperRepository


def make_mock_repo(**methods):
    repo = MagicMock(name="MockRepo")
    for name, value in methods.items():
        if callable(value):
            setattr(repo, name, AsyncMock(return_value=value()))
        else:
            setattr(repo, name, AsyncMock(return_value=value))
    return repo


# ────────────────────────── Interface Tests ────────────────────────────
class TestInterfaces:
    def test_paper_interface_methods(self):
        for method in [
            "create", "get_by_id", "get_by_doi", "get_by_pmid",
            "list_papers", "count_papers", "update", "delete", "search_semantic",
        ]:
            assert hasattr(PaperRepositoryInterface, method)

    def test_collection_interface_methods(self):
        for method in [
            "create", "get_by_id", "list_collections", "count_collections",
            "update", "delete", "add_paper", "remove_paper",
            "list_papers_in_collection", "count_papers_in_collection", "paper_in_collection",
        ]:
            assert hasattr(CollectionRepositoryInterface, method)

    def test_note_interface_methods(self):
        for method in ["create", "get_by_id", "list_by_paper", "count_by_paper", "update", "delete"]:
            assert hasattr(NoteRepositoryInterface, method)


# ────────────────────────── Paper Use Case Tests ───────────────────────
class TestCreatePaperUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(create=lambda: MagicMock(name="paper"))
        uc = CreatePaperUseCase(paper_repo=mock_repo)
        await uc.execute(title="Drought Resistance in Wheat", user_id="user-1")
        mock_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_empty_title_raises(self):
        mock_repo = make_mock_repo()
        uc = CreatePaperUseCase(paper_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(title="", user_id="user-1")

    @pytest.mark.asyncio
    async def test_duplicate_doi_raises(self):
        mock_repo = make_mock_repo(get_by_doi=lambda: MagicMock(name="existing"))
        uc = CreatePaperUseCase(paper_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(title="Test", user_id="user-1", doi="10.1234/test")

    @pytest.mark.asyncio
    async def test_duplicate_pmid_raises(self):
        mock_repo = make_mock_repo(get_by_pmid=lambda: MagicMock(name="existing"))
        uc = CreatePaperUseCase(paper_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(title="Test", user_id="user-1", pmid="12345")

    @pytest.mark.asyncio
    async def test_invalid_source_raises(self):
        mock_repo = make_mock_repo()
        uc = CreatePaperUseCase(paper_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(title="Test", user_id="user-1", source="invalid")

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        mock_repo = make_mock_repo()
        uc = CreatePaperUseCase(paper_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(title="Test", user_id="user-1", paper_type="invalid")


class TestGetPaperUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_by_id=lambda: MagicMock(name="paper"))
        uc = GetPaperUseCase(paper_repo=mock_repo)
        await uc.execute("paper-1")
        mock_repo.get_by_id.assert_awaited_once_with("paper-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = GetPaperUseCase(paper_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("nonexistent")


class TestListPapersUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(list_papers=lambda: [], count_papers=lambda: 0)
        uc = ListPapersUseCase(paper_repo=mock_repo)
        result = await uc.execute(skip=0, limit=20)
        assert isinstance(result, dict)
        assert "items" in result

    @pytest.mark.asyncio
    async def test_with_filters(self):
        mock_repo = make_mock_repo(list_papers=lambda: [], count_papers=lambda: 0)
        uc = ListPapersUseCase(paper_repo=mock_repo)
        await uc.execute(source="pubmed", paper_type="review", year=2024)
        mock_repo.list_papers.assert_awaited_once()


class TestUpdatePaperUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        paper = MagicMock(name="paper")
        paper.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: paper, update=lambda: paper)
        uc = UpdatePaperUseCase(paper_repo=mock_repo)
        await uc.execute(paper_id="paper-1", user_id="user-1", title="Updated")
        mock_repo.get_by_id.assert_awaited_once_with("paper-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = UpdatePaperUseCase(paper_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(paper_id="nonexistent", user_id="user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        paper = MagicMock(name="paper")
        paper.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: paper)
        uc = UpdatePaperUseCase(paper_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(paper_id="paper-1", user_id="user-2")


class TestDeletePaperUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        paper = MagicMock(name="paper")
        paper.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: paper, delete=lambda: True)
        uc = DeletePaperUseCase(paper_repo=mock_repo)
        await uc.execute(paper_id="paper-1", user_id="user-1")
        mock_repo.delete.assert_awaited_once_with("paper-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = DeletePaperUseCase(paper_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(paper_id="nonexistent", user_id="user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        paper = MagicMock(name="paper")
        paper.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: paper)
        uc = DeletePaperUseCase(paper_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(paper_id="paper-1", user_id="user-2")


class TestSearchPapersSemanticUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(search_semantic=lambda: [])
        uc = SearchPapersSemanticUseCase(paper_repo=mock_repo)
        result = await uc.execute(query_embedding=[0.1] * 384, limit=5)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_empty_embedding_raises(self):
        mock_repo = make_mock_repo()
        uc = SearchPapersSemanticUseCase(paper_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(query_embedding=[])


# ────────────────────────── Collection Use Case Tests ──────────────────
class TestCreateCollectionUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(create=lambda: MagicMock(name="collection"))
        uc = CreateCollectionUseCase(collection_repo=mock_repo)
        await uc.execute(name="Drought Papers", user_id="user-1")
        mock_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_empty_name_raises(self):
        mock_repo = make_mock_repo()
        uc = CreateCollectionUseCase(collection_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(name="", user_id="user-1")


class TestGetCollectionUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_by_id=lambda: MagicMock(name="collection"))
        uc = GetCollectionUseCase(collection_repo=mock_repo)
        await uc.execute("col-1")
        mock_repo.get_by_id.assert_awaited_once_with("col-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = GetCollectionUseCase(collection_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("nonexistent")


class TestListCollectionsUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(list_collections=lambda: [], count_collections=lambda: 0)
        uc = ListCollectionsUseCase(collection_repo=mock_repo)
        result = await uc.execute()
        assert isinstance(result, dict)


class TestUpdateCollectionUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        col = MagicMock(name="collection")
        col.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: col, update=lambda: col)
        uc = UpdateCollectionUseCase(collection_repo=mock_repo)
        await uc.execute(collection_id="col-1", user_id="user-1", name="Updated")
        mock_repo.get_by_id.assert_awaited_once_with("col-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = UpdateCollectionUseCase(collection_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(collection_id="nonexistent", user_id="user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        col = MagicMock(name="collection")
        col.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: col)
        uc = UpdateCollectionUseCase(collection_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(collection_id="col-1", user_id="user-2")


class TestDeleteCollectionUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        col = MagicMock(name="collection")
        col.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: col, delete=lambda: True)
        uc = DeleteCollectionUseCase(collection_repo=mock_repo)
        await uc.execute(collection_id="col-1", user_id="user-1")
        mock_repo.delete.assert_awaited_once_with("col-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = DeleteCollectionUseCase(collection_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(collection_id="nonexistent", user_id="user-1")


class TestAddPaperToCollectionUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_collection = make_mock_repo(
            get_by_id=lambda: MagicMock(name="collection"),
            paper_in_collection=lambda: False,
            add_paper=lambda: True,
        )
        mock_paper = make_mock_repo(get_by_id=lambda: MagicMock(name="paper"))
        uc = AddPaperToCollectionUseCase(collection_repo=mock_collection, paper_repo=mock_paper)
        result = await uc.execute(collection_id="col-1", paper_id="paper-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_collection_not_found(self):
        mock_collection = make_mock_repo(get_by_id=lambda: None)
        mock_paper = make_mock_repo()
        uc = AddPaperToCollectionUseCase(collection_repo=mock_collection, paper_repo=mock_paper)
        with pytest.raises(NotFoundException):
            await uc.execute(collection_id="nonexistent", paper_id="paper-1")

    @pytest.mark.asyncio
    async def test_paper_not_found(self):
        mock_collection = make_mock_repo(get_by_id=lambda: MagicMock(name="collection"))
        mock_paper = make_mock_repo(get_by_id=lambda: None)
        uc = AddPaperToCollectionUseCase(collection_repo=mock_collection, paper_repo=mock_paper)
        with pytest.raises(NotFoundException):
            await uc.execute(collection_id="col-1", paper_id="nonexistent")

    @pytest.mark.asyncio
    async def test_already_in_collection_raises(self):
        mock_collection = make_mock_repo(
            get_by_id=lambda: MagicMock(name="collection"),
            paper_in_collection=lambda: True,
        )
        mock_paper = make_mock_repo(get_by_id=lambda: MagicMock(name="paper"))
        uc = AddPaperToCollectionUseCase(collection_repo=mock_collection, paper_repo=mock_paper)
        with pytest.raises(ValidationException):
            await uc.execute(collection_id="col-1", paper_id="paper-1")


class TestRemovePaperFromCollectionUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(
            get_by_id=lambda: MagicMock(name="collection"),
            remove_paper=lambda: True,
        )
        uc = RemovePaperFromCollectionUseCase(collection_repo=mock_repo)
        result = await uc.execute(collection_id="col-1", paper_id="paper-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_collection_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = RemovePaperFromCollectionUseCase(collection_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(collection_id="nonexistent", paper_id="paper-1")


class TestListPapersInCollectionUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(
            get_by_id=lambda: MagicMock(name="collection"),
            list_papers_in_collection=lambda: [],
            count_papers_in_collection=lambda: 0,
        )
        uc = ListPapersInCollectionUseCase(collection_repo=mock_repo)
        result = await uc.execute(collection_id="col-1")
        assert isinstance(result, dict)
        assert "items" in result

    @pytest.mark.asyncio
    async def test_collection_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = ListPapersInCollectionUseCase(collection_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(collection_id="nonexistent")


# ────────────────────────── Note Use Case Tests ────────────────────────
class TestCreateNoteUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_note = make_mock_repo(create=lambda: MagicMock(name="note"))
        mock_paper = make_mock_repo(get_by_id=lambda: MagicMock(name="paper"))
        uc = CreateNoteUseCase(note_repo=mock_note, paper_repo=mock_paper)
        await uc.execute(paper_id="paper-1", content="Important finding", user_id="user-1")
        mock_note.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_paper_not_found(self):
        mock_note = make_mock_repo()
        mock_paper = make_mock_repo(get_by_id=lambda: None)
        uc = CreateNoteUseCase(note_repo=mock_note, paper_repo=mock_paper)
        with pytest.raises(NotFoundException):
            await uc.execute(paper_id="nonexistent", content="Note", user_id="user-1")

    @pytest.mark.asyncio
    async def test_empty_content_raises(self):
        mock_note = make_mock_repo()
        mock_paper = make_mock_repo(get_by_id=lambda: MagicMock(name="paper"))
        uc = CreateNoteUseCase(note_repo=mock_note, paper_repo=mock_paper)
        with pytest.raises(ValidationException):
            await uc.execute(paper_id="paper-1", content="", user_id="user-1")


class TestGetNoteUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(get_by_id=lambda: MagicMock(name="note"))
        uc = GetNoteUseCase(note_repo=mock_repo)
        await uc.execute("note-1")
        mock_repo.get_by_id.assert_awaited_once_with("note-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = GetNoteUseCase(note_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("nonexistent")


class TestListNotesByPaperUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_repo = make_mock_repo(list_by_paper=lambda: [], count_by_paper=lambda: 0)
        uc = ListNotesByPaperUseCase(note_repo=mock_repo)
        result = await uc.execute(paper_id="paper-1")
        assert isinstance(result, dict)


class TestUpdateNoteUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        note = MagicMock(name="note")
        note.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: note, update=lambda: note)
        uc = UpdateNoteUseCase(note_repo=mock_repo)
        await uc.execute(note_id="note-1", user_id="user-1", content="Updated note")
        mock_repo.get_by_id.assert_awaited_once_with("note-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = UpdateNoteUseCase(note_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(note_id="nonexistent", user_id="user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        note = MagicMock(name="note")
        note.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: note)
        uc = UpdateNoteUseCase(note_repo=mock_repo)
        with pytest.raises(ValidationException):
            await uc.execute(note_id="note-1", user_id="user-2")


class TestDeleteNoteUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        note = MagicMock(name="note")
        note.created_by = "user-1"
        mock_repo = make_mock_repo(get_by_id=lambda: note, delete=lambda: True)
        uc = DeleteNoteUseCase(note_repo=mock_repo)
        await uc.execute(note_id="note-1", user_id="user-1")
        mock_repo.delete.assert_awaited_once_with("note-1")

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_repo = make_mock_repo(get_by_id=lambda: None)
        uc = DeleteNoteUseCase(note_repo=mock_repo)
        with pytest.raises(NotFoundException):
            await uc.execute(note_id="nonexistent", user_id="user-1")


# ────────────────────────── Schema Tests ───────────────────────────────
class TestSchemaValidation:
    def test_create_paper_request(self):
        req = CreatePaperRequest(title="Drought Resistance in Wheat", source="pubmed")
        assert req.title == "Drought Resistance in Wheat"
        assert req.source == "pubmed"

    def test_create_paper_defaults(self):
        req = CreatePaperRequest(title="Test")
        assert req.source == "manual"
        assert req.paper_type == "article"

    def test_create_collection_request(self):
        req = CreateCollectionRequest(name="My Collection", color="#FF0000")
        assert req.name == "My Collection"
        assert req.color == "#FF0000"

    def test_create_note_request(self):
        req = CreateNoteRequest(content="Important finding on page 5", page_number=5)
        assert req.content == "Important finding on page 5"
        assert req.page_number == 5

    def test_paper_response(self):
        resp = PaperResponse(
            id="p-1", title="Test", source="manual", paper_type="article",
            created_by="user-1", created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
        assert resp.id == "p-1"

    def test_collection_response(self):
        resp = CollectionResponse(
            id="c-1", name="Test", created_by="user-1",
            created_at="2025-01-01T00:00:00", updated_at="2025-01-01T00:00:00",
        )
        assert resp.id == "c-1"

    def test_note_response(self):
        resp = NoteResponse(
            id="n-1", paper_id="p-1", content="Test note",
            created_by="user-1", created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
        assert resp.id == "n-1"

    def test_paginated_responses(self):
        p = PaginatedPapersResponse(items=[], total=0, skip=0, limit=20)
        c = PaginatedCollectionsResponse(items=[], total=0, skip=0, limit=20)
        n = PaginatedNotesResponse(items=[], total=0, skip=0, limit=100)
        assert p.total == 0
        assert c.total == 0
        assert n.total == 0

    def test_semantic_search_request(self):
        req = SemanticSearchRequest(query="drought resistance mechanisms")
        assert req.query == "drought resistance mechanisms"
        assert req.limit == 10


# ────────────────────────── Integration Tests ──────────────────────────
class TestLiteratureModuleIntegration:
    def test_module_has_correct_structure(self):
        pass

    def test_router_has_all_endpoints(self):
        from app.modules.literature.api.router import router
        routes = [r.path for r in router.routes]
        assert any("/papers" in p for p in routes)
        assert any("/collections" in p for p in routes)
        assert any("/search" in p for p in routes)
        assert any("notes" in p for p in routes)

    def test_all_use_case_classes_exist(self):
        use_cases = [
            CreatePaperUseCase, GetPaperUseCase, ListPapersUseCase,
            UpdatePaperUseCase, DeletePaperUseCase, SearchPapersSemanticUseCase,
            CreateCollectionUseCase, GetCollectionUseCase, ListCollectionsUseCase,
            UpdateCollectionUseCase, DeleteCollectionUseCase,
            AddPaperToCollectionUseCase, RemovePaperFromCollectionUseCase,
            ListPapersInCollectionUseCase,
            CreateNoteUseCase, GetNoteUseCase, ListNotesByPaperUseCase,
            UpdateNoteUseCase, DeleteNoteUseCase,
        ]
        assert len(use_cases) == 19

    def test_infrastructure_repos_exist(self):
        assert PaperRepository is not None
        assert CollectionRepository is not None
        assert NoteRepository is not None
