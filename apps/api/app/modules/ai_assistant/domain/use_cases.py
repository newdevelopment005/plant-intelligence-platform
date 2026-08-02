from datetime import UTC, datetime

from app.core.exceptions import NotFoundException, ValidationException
from app.modules.ai_assistant.domain.interfaces import (
    ConversationRepositoryInterface,
    MessageRepositoryInterface,
)
from app.modules.ai_assistant.domain.models import ConversationModel, MessageModel


class CreateConversationUseCase:
    def __init__(self, conversation_repo: ConversationRepositoryInterface):
        self.conversation_repo = conversation_repo

    async def execute(
        self,
        title: str,
        user_id: str,
        description: str | None = None,
        model_used: str | None = None,
        tags: list[str] | None = None,
        project_id: str | None = None,
    ) -> ConversationModel:
        if not title or not title.strip():
            raise ValidationException("Conversation title is required")
        if len(title.strip()) > 500:
            raise ValidationException("Conversation title must be less than 500 characters")

        conversation = ConversationModel(
            title=title.strip(),
            description=description.strip() if description else None,
            status="active",
            model_used=model_used,
            tags=tags,
            project_id=project_id,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.conversation_repo.create(conversation)


class GetConversationUseCase:
    def __init__(self, conversation_repo: ConversationRepositoryInterface):
        self.conversation_repo = conversation_repo

    async def execute(self, conversation_id: str) -> ConversationModel:
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException("Conversation", conversation_id)
        return conversation


class ListConversationsUseCase:
    def __init__(self, conversation_repo: ConversationRepositoryInterface):
        self.conversation_repo = conversation_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        if status is not None:
            valid_statuses = ("active", "archived", "deleted")
            if status not in valid_statuses:
                raise ValidationException(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        conversations = await self.conversation_repo.list_conversations(
            skip=skip, limit=limit, project_id=project_id,
            status=status, search=search, user_id=user_id,
        )
        total = await self.conversation_repo.count_conversations(
            project_id=project_id, status=status, search=search, user_id=user_id,
        )
        return {
            "items": [
                {
                    "id": str(c.id),
                    "title": c.title,
                    "description": c.description,
                    "status": c.status,
                    "model_used": c.model_used,
                    "tags": c.tags,
                    "message_count": c.message_count,
                    "project_id": str(c.project_id) if c.project_id else None,
                    "created_by": str(c.created_by),
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                }
                for c in conversations
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateConversationUseCase:
    def __init__(self, conversation_repo: ConversationRepositoryInterface):
        self.conversation_repo = conversation_repo

    async def execute(
        self,
        conversation_id: str,
        user_id: str,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        tags: list[str] | None = None,
    ) -> ConversationModel:
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException("Conversation", conversation_id)

        if str(conversation.created_by) != user_id:
            raise ValidationException("Only the creator can update this conversation")

        if title is not None:
            if not title.strip():
                raise ValidationException("Conversation title cannot be empty")
            conversation.title = title.strip()
        if description is not None:
            conversation.description = description.strip() if description else None
        if status is not None:
            valid_statuses = ("active", "archived", "deleted")
            if status not in valid_statuses:
                raise ValidationException(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            conversation.status = status
        if tags is not None:
            conversation.tags = tags

        conversation.updated_at = datetime.now(UTC)
        return await self.conversation_repo.update(conversation)


class DeleteConversationUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryInterface,
        message_repo: MessageRepositoryInterface,
    ):
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo

    async def execute(self, conversation_id: str, user_id: str) -> bool:
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException("Conversation", conversation_id)

        if str(conversation.created_by) != user_id:
            raise ValidationException("Only the creator can delete this conversation")

        messages = await self.message_repo.list_by_conversation(conversation_id, limit=1000)
        for msg in messages:
            await self.message_repo.delete(str(msg.id))

        return await self.conversation_repo.delete(conversation_id)


class SendMessageUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryInterface,
        message_repo: MessageRepositoryInterface,
    ):
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo

    async def execute(
        self,
        conversation_id: str,
        content: str,
        user_id: str,
    ) -> MessageModel:
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException("Conversation", conversation_id)

        if str(conversation.created_by) != user_id:
            raise ValidationException("Only the conversation creator can send messages")

        if conversation.status != "active":
            raise ValidationException("Cannot send messages to an archived conversation")

        if not content or not content.strip():
            raise ValidationException("Message content is required")

        user_message = MessageModel(
            conversation_id=conversation_id,
            role="user",
            content=content.strip(),
            created_at=datetime.now(UTC),
        )
        user_message = await self.message_repo.create(user_message)
        await self.conversation_repo.increment_message_count(conversation_id)

        assistant_content = f"[AI response placeholder for: {content.strip()[:100]}]"
        assistant_message = MessageModel(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_content,
            model_used=conversation.model_used,
            created_at=datetime.now(UTC),
        )
        assistant_message = await self.message_repo.create(assistant_message)
        await self.conversation_repo.increment_message_count(conversation_id)

        return assistant_message


class ListMessagesUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryInterface,
        message_repo: MessageRepositoryInterface,
    ):
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo

    async def execute(
        self,
        conversation_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException("Conversation", conversation_id)

        messages = await self.message_repo.list_by_conversation(
            conversation_id, skip=skip, limit=limit
        )
        total = await self.message_repo.count_by_conversation(conversation_id)

        return {
            "items": [
                {
                    "id": str(m.id),
                    "conversation_id": str(m.conversation_id),
                    "role": m.role,
                    "content": m.content,
                    "model_used": m.model_used,
                    "tokens_used": m.tokens_used,
                    "sources": m.sources,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class SummarizeLiteratureUseCase:
    async def execute(
        self,
        paper_ids: list[str],
        user_id: str,
        focus_areas: list[str] | None = None,
    ) -> dict:
        if not paper_ids:
            raise ValidationException("At least one paper ID is required")

        summary = (
            f"[Literature summary placeholder for {len(paper_ids)} papers"
            + (f" focusing on {', '.join(focus_areas)}" if focus_areas else "")
            + "]"
        )
        return {
            "summary": summary,
            "key_findings": [],
            "methodologies": [],
            "gaps_identified": [],
            "paper_count": len(paper_ids),
        }


class RecommendGenesUseCase:
    async def execute(
        self,
        trait_description: str,
        species: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        if not trait_description or not trait_description.strip():
            raise ValidationException("Trait description is required")

        return {
            "recommendations": [],
            "trait": trait_description.strip(),
            "species": species,
            "reasoning": f"[Gene recommendation placeholder for trait: {trait_description[:100]}]",
        }


class DesignExperimentUseCase:
    async def execute(
        self,
        research_question: str,
        user_id: str,
        species: str | None = None,
        variables: list[str] | None = None,
        constraints: dict | None = None,
    ) -> dict:
        if not research_question or not research_question.strip():
            raise ValidationException("Research question is required")

        return {
            "experiment_design": {
                "title": f"Experiment for: {research_question[:100]}",
                "objective": research_question.strip(),
                "species": species,
                "variables": variables or [],
                "constraints": constraints or {},
                "design_type": "randomized_complete_block",
                "replications": 3,
                "treatments": [],
                "controls": [],
                "data_collection_plan": [],
                "statistical_analysis": [],
            },
            "suggestions": [],
        }


class AnalyzeImageUseCase:
    async def execute(
        self,
        image_url: str | None = None,
        image_base64: str | None = None,
        analysis_type: str = "general",
        user_id: str | None = None,
    ) -> dict:
        if not image_url and not image_base64:
            raise ValidationException("Either image_url or image_base64 is required")

        valid_types = ("general", "phenotype", "disease", "growth_stage", "morphology")
        if analysis_type not in valid_types:
            raise ValidationException(f"Invalid analysis type. Must be one of: {', '.join(valid_types)}")

        return {
            "analysis": {
                "type": analysis_type,
                "results": {},
                "confidence": 0.0,
                "annotations": [],
            },
            "interpretation": f"[Image analysis placeholder for type: {analysis_type}]",
        }
