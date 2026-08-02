from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.ai_assistant.api.schemas import (
    AnalyzeImageRequest,
    ConversationResponse,
    CreateConversationRequest,
    DesignExperimentRequest,
    ExperimentDesignResponse,
    GeneRecommendationResponse,
    ImageAnalysisResponse,
    LiteratureSummaryResponse,
    MessageResponse,
    PaginatedConversationsResponse,
    PaginatedMessagesResponse,
    RecommendGenesRequest,
    SendMessageRequest,
    SummarizeLiteratureRequest,
    UpdateConversationRequest,
)
from app.modules.ai_assistant.domain.interfaces import (
    ConversationRepositoryInterface,
    MessageRepositoryInterface,
)
from app.modules.ai_assistant.domain.use_cases import (
    AnalyzeImageUseCase,
    CreateConversationUseCase,
    DeleteConversationUseCase,
    DesignExperimentUseCase,
    GetConversationUseCase,
    ListConversationsUseCase,
    ListMessagesUseCase,
    RecommendGenesUseCase,
    SendMessageUseCase,
    SummarizeLiteratureUseCase,
    UpdateConversationUseCase,
)


def make_mock_repo(**methods):
    repo = MagicMock(name="MockRepo")
    for method_name, value in methods.items():
        if callable(value):
            try:
                result = value()
                setattr(repo, method_name, AsyncMock(return_value=result))
            except TypeError:
                setattr(repo, method_name, AsyncMock(side_effect=value))
        else:
            setattr(repo, method_name, AsyncMock(return_value=value))
    return repo


def _make_conversation(**overrides):
    defaults = {
        "id": "conv-1",
        "title": "Test Conversation",
        "description": "A test",
        "status": "active",
        "model_used": "gpt-4",
        "tags": ["test"],
        "message_count": 0,
        "project_id": "proj-1",
        "created_by": "user-1",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def _make_message(**overrides):
    defaults = {
        "id": "msg-1",
        "conversation_id": "conv-1",
        "role": "assistant",
        "content": "Hello!",
        "model_used": "gpt-4",
        "tokens_used": 100,
        "sources": None,
        "created_at": datetime.now(UTC),
        "metadata_json": None,
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


# ────────────────────────── Interfaces ────────────────────────────────
class TestInterfaces:
    def test_conversation_interface_methods(self):
        methods = [
            "create", "get_by_id", "list_conversations", "count_conversations",
            "update", "delete", "increment_message_count",
        ]
        for m in methods:
            assert hasattr(ConversationRepositoryInterface, m)

    def test_message_interface_methods(self):
        methods = ["create", "get_by_id", "list_by_conversation", "count_by_conversation", "delete"]
        for m in methods:
            assert hasattr(MessageRepositoryInterface, m)


# ────────────────────────── CreateConversationUseCase ─────────────────
class TestCreateConversationUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        repo = make_mock_repo(create=lambda: _make_conversation())
        uc = CreateConversationUseCase(conversation_repo=repo)
        result = await uc.execute(
            title="My Conversation", user_id="user-1", description="desc",
            model_used="gpt-4", tags=["test"], project_id="proj-1",
        )
        assert result.title == "Test Conversation"
        repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_empty_title_raises(self):
        repo = make_mock_repo()
        uc = CreateConversationUseCase(conversation_repo=repo)
        with pytest.raises(ValidationException, match="title is required"):
            await uc.execute(title="  ", user_id="user-1")

    @pytest.mark.asyncio
    async def test_long_title_raises(self):
        repo = make_mock_repo()
        uc = CreateConversationUseCase(conversation_repo=repo)
        with pytest.raises(ValidationException, match="less than 500"):
            await uc.execute(title="x" * 501, user_id="user-1")


# ────────────────────────── GetConversationUseCase ───────────────────
class TestGetConversationUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        conv = _make_conversation()
        repo = make_mock_repo(get_by_id=lambda eid: conv)
        uc = GetConversationUseCase(conversation_repo=repo)
        result = await uc.execute("conv-1")
        assert result.id == "conv-1"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = GetConversationUseCase(conversation_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing")


# ────────────────────────── ListConversationsUseCase ──────────────────
class TestListConversationsUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        conv = _make_conversation()
        repo = make_mock_repo(
            list_conversations=lambda: [conv],
            count_conversations=lambda: 1,
        )
        uc = ListConversationsUseCase(conversation_repo=repo)
        result = await uc.execute(user_id="user-1")
        assert result["total"] == 1
        assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_invalid_status_raises(self):
        repo = make_mock_repo()
        uc = ListConversationsUseCase(conversation_repo=repo)
        with pytest.raises(ValidationException, match="Invalid status"):
            await uc.execute(status="bogus")


# ────────────────────────── UpdateConversationUseCase ─────────────────
class TestUpdateConversationUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        conv = _make_conversation()
        repo = make_mock_repo(
            get_by_id=lambda eid: conv,
            update=lambda c: c,
        )
        uc = UpdateConversationUseCase(conversation_repo=repo)
        result = await uc.execute("conv-1", "user-1", title="New Title")
        assert result.title == "New Title"

    @pytest.mark.asyncio
    async def test_not_found(self):
        repo = make_mock_repo(get_by_id=lambda eid: None)
        uc = UpdateConversationUseCase(conversation_repo=repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1", title="x")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        conv = _make_conversation(created_by="user-1")
        repo = make_mock_repo(get_by_id=lambda eid: conv)
        uc = UpdateConversationUseCase(conversation_repo=repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("conv-1", "user-2", title="x")

    @pytest.mark.asyncio
    async def test_empty_title_raises(self):
        conv = _make_conversation()
        repo = make_mock_repo(get_by_id=lambda eid: conv)
        uc = UpdateConversationUseCase(conversation_repo=repo)
        with pytest.raises(ValidationException, match="cannot be empty"):
            await uc.execute("conv-1", "user-1", title="  ")

    @pytest.mark.asyncio
    async def test_invalid_status_raises(self):
        conv = _make_conversation()
        repo = make_mock_repo(get_by_id=lambda eid: conv)
        uc = UpdateConversationUseCase(conversation_repo=repo)
        with pytest.raises(ValidationException, match="Invalid status"):
            await uc.execute("conv-1", "user-1", status="bogus")


# ────────────────────────── DeleteConversationUseCase ─────────────────
class TestDeleteConversationUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        conv = _make_conversation()
        msg = _make_message()
        conv_repo = make_mock_repo(
            get_by_id=lambda eid: conv,
            delete=lambda eid: True,
        )
        msg_repo = make_mock_repo(
            list_by_conversation=lambda: [msg],
            delete=lambda mid: True,
        )
        uc = DeleteConversationUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
        result = await uc.execute("conv-1", "user-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_not_found(self):
        conv_repo = make_mock_repo(get_by_id=lambda eid: None)
        msg_repo = make_mock_repo()
        uc = DeleteConversationUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        conv = _make_conversation(created_by="user-1")
        conv_repo = make_mock_repo(get_by_id=lambda eid: conv)
        msg_repo = make_mock_repo()
        uc = DeleteConversationUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
        with pytest.raises(ValidationException, match="Only the creator"):
            await uc.execute("conv-1", "user-2")


# ────────────────────────── SendMessageUseCase ────────────────────────
class TestSendMessageUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        conv = _make_conversation()
        assistant_msg = _make_message()
        conv_repo = make_mock_repo(
            get_by_id=lambda eid: conv,
            increment_message_count=lambda cid: None,
        )
        msg_repo = make_mock_repo(
            create=lambda m: assistant_msg,
        )
        uc = SendMessageUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
        result = await uc.execute("conv-1", "Hello AI", "user-1")
        assert result.role == "assistant"
        assert msg_repo.create.await_count == 2

    @pytest.mark.asyncio
    async def test_conversation_not_found(self):
        conv_repo = make_mock_repo(get_by_id=lambda eid: None)
        msg_repo = make_mock_repo()
        uc = SendMessageUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing", "hi", "user-1")

    @pytest.mark.asyncio
    async def test_wrong_user_raises(self):
        conv = _make_conversation(created_by="user-1")
        conv_repo = make_mock_repo(get_by_id=lambda eid: conv)
        msg_repo = make_mock_repo()
        uc = SendMessageUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
        with pytest.raises(ValidationException, match="Only the conversation creator"):
            await uc.execute("conv-1", "hi", "user-2")

    @pytest.mark.asyncio
    async def test_archived_conversation_raises(self):
        conv = _make_conversation(status="archived")
        conv_repo = make_mock_repo(get_by_id=lambda eid: conv)
        msg_repo = make_mock_repo()
        uc = SendMessageUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
        with pytest.raises(ValidationException, match="archived"):
            await uc.execute("conv-1", "hi", "user-1")

    @pytest.mark.asyncio
    async def test_empty_content_raises(self):
        conv = _make_conversation()
        conv_repo = make_mock_repo(get_by_id=lambda eid: conv)
        msg_repo = make_mock_repo()
        uc = SendMessageUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
        with pytest.raises(ValidationException, match="content is required"):
            await uc.execute("conv-1", "  ", "user-1")


# ────────────────────────── ListMessagesUseCase ───────────────────────
class TestListMessagesUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        conv = _make_conversation()
        msg = _make_message()
        conv_repo = make_mock_repo(get_by_id=lambda eid: conv)
        msg_repo = make_mock_repo(
            list_by_conversation=lambda: [msg],
            count_by_conversation=lambda: 1,
        )
        uc = ListMessagesUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
        result = await uc.execute("conv-1")
        assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_conversation_not_found(self):
        conv_repo = make_mock_repo(get_by_id=lambda eid: None)
        msg_repo = make_mock_repo()
        uc = ListMessagesUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
        with pytest.raises(NotFoundException):
            await uc.execute("missing")


# ────────────────────────── SummarizeLiteratureUseCase ────────────────
class TestSummarizeLiteratureUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        uc = SummarizeLiteratureUseCase()
        result = await uc.execute(paper_ids=["p1", "p2"], user_id="u1")
        assert result["paper_count"] == 2
        assert isinstance(result["summary"], str)

    @pytest.mark.asyncio
    async def test_empty_paper_ids_raises(self):
        uc = SummarizeLiteratureUseCase()
        with pytest.raises(ValidationException, match="At least one paper"):
            await uc.execute(paper_ids=[], user_id="u1")

    @pytest.mark.asyncio
    async def test_with_focus_areas(self):
        uc = SummarizeLiteratureUseCase()
        result = await uc.execute(
            paper_ids=["p1"], user_id="u1", focus_areas=["drought", "genomics"]
        )
        assert "drought" in result["summary"]


# ────────────────────────── RecommendGenesUseCase ─────────────────────
class TestRecommendGenesUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        uc = RecommendGenesUseCase()
        result = await uc.execute(trait_description="drought tolerance", species="wheat")
        assert result["species"] == "wheat"
        assert isinstance(result["reasoning"], str)

    @pytest.mark.asyncio
    async def test_empty_trait_raises(self):
        uc = RecommendGenesUseCase()
        with pytest.raises(ValidationException, match="Trait description is required"):
            await uc.execute(trait_description="  ")


# ────────────────────────── DesignExperimentUseCase ───────────────────
class TestDesignExperimentUseCase:
    @pytest.mark.asyncio
    async def test_success(self):
        uc = DesignExperimentUseCase()
        result = await uc.execute(
            research_question="What is the effect of nitrogen on yield?",
            user_id="u1",
            species="rice",
            variables=["nitrogen_level", "yield"],
        )
        assert "experiment_design" in result
        assert result["experiment_design"]["species"] == "rice"

    @pytest.mark.asyncio
    async def test_empty_question_raises(self):
        uc = DesignExperimentUseCase()
        with pytest.raises(ValidationException, match="Research question is required"):
            await uc.execute(research_question="  ", user_id="u1")


# ────────────────────────── AnalyzeImageUseCase ───────────────────────
class TestAnalyzeImageUseCase:
    @pytest.mark.asyncio
    async def test_success_url(self):
        uc = AnalyzeImageUseCase()
        result = await uc.execute(image_url="http://example.com/img.jpg", analysis_type="disease")
        assert result["analysis"]["type"] == "disease"

    @pytest.mark.asyncio
    async def test_success_base64(self):
        uc = AnalyzeImageUseCase()
        result = await uc.execute(image_base64="abc123", analysis_type="phenotype")
        assert result["analysis"]["type"] == "phenotype"

    @pytest.mark.asyncio
    async def test_no_image_raises(self):
        uc = AnalyzeImageUseCase()
        with pytest.raises(ValidationException, match="Either image_url or image_base64"):
            await uc.execute()

    @pytest.mark.asyncio
    async def test_invalid_type_raises(self):
        uc = AnalyzeImageUseCase()
        with pytest.raises(ValidationException, match="Invalid analysis type"):
            await uc.execute(image_url="http://x.com/img.jpg", analysis_type="invalid_type")


# ────────────────────────── Schema Validation ─────────────────────────
class TestSchemaValidation:
    def test_create_conversation_request(self):
        req = CreateConversationRequest(title="Test")
        assert req.title == "Test"
        assert req.description is None

    def test_create_conversation_request_defaults(self):
        req = CreateConversationRequest(title="Hello")
        assert req.model_used is None
        assert req.tags is None

    def test_update_conversation_request(self):
        req = UpdateConversationRequest(title="New")
        assert req.title == "New"
        assert req.status is None

    def test_send_message_request(self):
        req = SendMessageRequest(content="Hello AI")
        assert req.content == "Hello AI"

    def test_send_message_request_empty_rejects(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            SendMessageRequest(content="")

    def test_summarize_literature_request(self):
        req = SummarizeLiteratureRequest(paper_ids=["p1", "p2"])
        assert len(req.paper_ids) == 2

    def test_recommend_genes_request(self):
        req = RecommendGenesRequest(trait_description="yield")
        assert req.trait_description == "yield"

    def test_design_experiment_request(self):
        req = DesignExperimentRequest(research_question="Test?")
        assert req.research_question == "Test?"

    def test_analyze_image_request(self):
        req = AnalyzeImageRequest(image_url="http://x.com/img.jpg")
        assert req.analysis_type == "general"

    def test_conversation_response(self):
        resp = ConversationResponse(
            id="c1", title="T", status="active", created_by="u1",
            created_at="2025-01-01T00:00:00Z", updated_at="2025-01-01T00:00:00Z",
        )
        assert resp.id == "c1"

    def test_message_response(self):
        resp = MessageResponse(
            id="m1", conversation_id="c1", role="user", content="Hi",
            created_at="2025-01-01T00:00:00Z",
        )
        assert resp.role == "user"

    def test_literature_summary_response(self):
        resp = LiteratureSummaryResponse(
            summary="s", key_findings=[], methodologies=[], gaps_identified=[], paper_count=1,
        )
        assert resp.paper_count == 1

    def test_gene_recommendation_response(self):
        resp = GeneRecommendationResponse(
            recommendations=[], trait="yield", reasoning="r",
        )
        assert resp.trait == "yield"

    def test_experiment_design_response(self):
        resp = ExperimentDesignResponse(experiment_design={}, suggestions=[])
        assert resp.experiment_design == {}

    def test_image_analysis_response(self):
        resp = ImageAnalysisResponse(analysis={}, interpretation="i")
        assert resp.interpretation == "i"

    def test_paginated_conversations_response(self):
        resp = PaginatedConversationsResponse(items=[], total=0, skip=0, limit=20)
        assert resp.total == 0

    def test_paginated_messages_response(self):
        resp = PaginatedMessagesResponse(items=[], total=0, skip=0, limit=100)
        assert resp.total == 0


# ────────────────────────── Integration Tests ─────────────────────────
class TestAIAssistantModuleIntegration:
    def test_module_has_correct_structure(self):
        from app.modules.ai_assistant.api import schemas
        from app.modules.ai_assistant.api.router import router
        from app.modules.ai_assistant.domain import interfaces, models

        assert hasattr(models, "ConversationModel")
        assert hasattr(models, "MessageModel")
        assert hasattr(interfaces, "ConversationRepositoryInterface")
        assert hasattr(interfaces, "MessageRepositoryInterface")
        assert hasattr(schemas, "CreateConversationRequest")
        assert router is not None

    def test_router_has_all_endpoints(self):
        from app.modules.ai_assistant.api.router import router
        routes = {r.path for r in router.routes}
        expected = [
            "/api/v1/ai/conversations",
            "/api/v1/ai/conversations/{conversation_id}",
            "/api/v1/ai/conversations/{conversation_id}/messages",
            "/api/v1/ai/summarize-literature",
            "/api/v1/ai/recommend-genes",
            "/api/v1/ai/design-experiment",
            "/api/v1/ai/analyze-image",
        ]
        for ep in expected:
            assert ep in routes, f"Missing endpoint: {ep}"

    def test_all_use_case_classes_exist(self):
        from app.modules.ai_assistant.domain import use_cases
        expected = [
            "CreateConversationUseCase", "GetConversationUseCase",
            "ListConversationsUseCase", "UpdateConversationUseCase",
            "DeleteConversationUseCase", "SendMessageUseCase",
            "ListMessagesUseCase", "SummarizeLiteratureUseCase",
            "RecommendGenesUseCase", "DesignExperimentUseCase",
            "AnalyzeImageUseCase",
        ]
        for name in expected:
            assert hasattr(use_cases, name), f"Missing use case: {name}"

    def test_infrastructure_repos_exist(self):
        from app.modules.ai_assistant.infrastructure import (
            conversation_repository,
            message_repository,
        )
        assert hasattr(conversation_repository, "ConversationRepository")
        assert hasattr(message_repository, "MessageRepository")
