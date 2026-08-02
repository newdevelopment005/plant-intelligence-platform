from abc import ABC, abstractmethod

from app.modules.ai_assistant.domain.models import ConversationModel, MessageModel


class ConversationRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, conversation: ConversationModel) -> ConversationModel: ...

    @abstractmethod
    async def get_by_id(self, conversation_id: str) -> ConversationModel | None: ...

    @abstractmethod
    async def list_conversations(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[ConversationModel]: ...

    @abstractmethod
    async def count_conversations(
        self,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def update(self, conversation: ConversationModel) -> ConversationModel: ...

    @abstractmethod
    async def delete(self, conversation_id: str) -> bool: ...

    @abstractmethod
    async def increment_message_count(self, conversation_id: str) -> None: ...


class MessageRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, message: MessageModel) -> MessageModel: ...

    @abstractmethod
    async def get_by_id(self, message_id: str) -> MessageModel | None: ...

    @abstractmethod
    async def list_by_conversation(
        self, conversation_id: str, skip: int = 0, limit: int = 100
    ) -> list[MessageModel]: ...

    @abstractmethod
    async def count_by_conversation(self, conversation_id: str) -> int: ...

    @abstractmethod
    async def delete(self, message_id: str) -> bool: ...
