from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.database import get_db
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

router = APIRouter()


# ────────────────────────── Conversations ──────────────────────────────
@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: CreateConversationRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.ai_assistant.infrastructure.conversation_repository import (
        ConversationRepository,
    )
    repo = ConversationRepository(db)
    uc = CreateConversationUseCase(conversation_repo=repo)
    return await uc.execute(
        title=request.title,
        user_id=current_user["id"],
        description=request.description,
        model_used=request.model_used,
        tags=request.tags,
        project_id=request.project_id,
    )


@router.get("/conversations", response_model=PaginatedConversationsResponse)
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    project_id: str | None = None,
    status_filter: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.ai_assistant.infrastructure.conversation_repository import (
        ConversationRepository,
    )
    repo = ConversationRepository(db)
    uc = ListConversationsUseCase(conversation_repo=repo)
    result = await uc.execute(
        skip=skip, limit=limit, project_id=project_id,
        status=status_filter, search=search, user_id=current_user["id"],
    )
    return PaginatedConversationsResponse(**result)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.ai_assistant.infrastructure.conversation_repository import (
        ConversationRepository,
    )
    repo = ConversationRepository(db)
    uc = GetConversationUseCase(conversation_repo=repo)
    return await uc.execute(conversation_id)


@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.ai_assistant.infrastructure.conversation_repository import (
        ConversationRepository,
    )
    repo = ConversationRepository(db)
    uc = UpdateConversationUseCase(conversation_repo=repo)
    return await uc.execute(
        conversation_id=conversation_id,
        user_id=current_user["id"],
        title=request.title,
        description=request.description,
        status=request.status,
        tags=request.tags,
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.ai_assistant.infrastructure.conversation_repository import (
        ConversationRepository,
    )
    from app.modules.ai_assistant.infrastructure.message_repository import MessageRepository
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)
    uc = DeleteConversationUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
    await uc.execute(conversation_id=conversation_id, user_id=current_user["id"])


# ────────────────────────── Messages ──────────────────────────────────
@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.ai_assistant.infrastructure.conversation_repository import (
        ConversationRepository,
    )
    from app.modules.ai_assistant.infrastructure.message_repository import MessageRepository
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)
    uc = SendMessageUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
    return await uc.execute(
        conversation_id=conversation_id,
        content=request.content,
        user_id=current_user["id"],
    )


@router.get("/conversations/{conversation_id}/messages", response_model=PaginatedMessagesResponse)
async def list_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.ai_assistant.infrastructure.conversation_repository import (
        ConversationRepository,
    )
    from app.modules.ai_assistant.infrastructure.message_repository import MessageRepository
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)
    uc = ListMessagesUseCase(conversation_repo=conv_repo, message_repo=msg_repo)
    result = await uc.execute(
        conversation_id=conversation_id, skip=skip, limit=limit,
    )
    return PaginatedMessagesResponse(**result)


# ────────────────────────── AI Tools ──────────────────────────────────
@router.post("/summarize-literature", response_model=LiteratureSummaryResponse)
async def summarize_literature(
    request: SummarizeLiteratureRequest,
    current_user=Depends(get_current_active_user),
):
    uc = SummarizeLiteratureUseCase()
    return await uc.execute(
        paper_ids=request.paper_ids,
        user_id=current_user["id"],
        focus_areas=request.focus_areas,
    )


@router.post("/recommend-genes", response_model=GeneRecommendationResponse)
async def recommend_genes(
    request: RecommendGenesRequest,
    current_user=Depends(get_current_active_user),
):
    uc = RecommendGenesUseCase()
    return await uc.execute(
        trait_description=request.trait_description,
        species=request.species,
        user_id=current_user["id"],
    )


@router.post("/design-experiment", response_model=ExperimentDesignResponse)
async def design_experiment(
    request: DesignExperimentRequest,
    current_user=Depends(get_current_active_user),
):
    uc = DesignExperimentUseCase()
    return await uc.execute(
        research_question=request.research_question,
        user_id=current_user["id"],
        species=request.species,
        variables=request.variables,
        constraints=request.constraints,
    )


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(
    request: AnalyzeImageRequest,
    current_user=Depends(get_current_active_user),
):
    uc = AnalyzeImageUseCase()
    return await uc.execute(
        image_url=request.image_url,
        image_base64=request.image_base64,
        analysis_type=request.analysis_type,
        user_id=current_user["id"],
    )
