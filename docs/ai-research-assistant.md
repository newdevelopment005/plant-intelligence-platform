# AI Research Assistant Module

## Overview

The AI Research Assistant module provides an integrated AI-powered chat and analysis layer for the Plant Intelligence Platform. It manages conversations with the AI assistant, stores message history, and exposes specialized AI tools for literature summarization, gene recommendation, experiment design, and image analysis.

## Architecture

```
ai_assistant/
├── domain/
│   ├── models.py          # ConversationModel, MessageModel
│   ├── interfaces.py      # ConversationRepositoryInterface, MessageRepositoryInterface
│   └── use_cases.py       # 11 use cases
├── infrastructure/
│   ├── conversation_repository.py
│   ├── message_repository.py
│   └── __init__.py
└── api/
    ├── router.py           # 11 REST endpoints
    └── schemas.py          # 14 Pydantic schemas
```

## Domain Models

### ConversationModel

Represents a chat session with the AI assistant.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `title` | str (required) | Conversation title |
| `description` | str \| None | Description text |
| `status` | str | `active`, `archived`, or `deleted` |
| `model_used` | str \| None | AI model identifier (e.g., `gpt-4`) |
| `tags` | list[str] \| None | Categorization tags |
| `message_count` | int | Number of messages (auto-incremented) |
| `project_id` | UUID \| None | Owning project |
| `created_by` | UUID | Creator user ID |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

### MessageModel

Represents a single message within a conversation.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated primary key |
| `conversation_id` | UUID | Parent conversation |
| `role` | str | `user` or `assistant` |
| `content` | str (required) | Message text |
| `model_used` | str \| None | AI model used for this message |
| `tokens_used` | int \| None | Token count |
| `sources` | list[dict] \| None | Cited sources (JSONB) |
| `created_at` | datetime | Creation timestamp |
| `metadata_json` | dict \| None | Arbitrary metadata (JSONB) |

## Interfaces

### ConversationRepositoryInterface

```python
class ConversationRepositoryInterface(ABC):
    async def create(self, conversation) -> ConversationModel
    async def get_by_id(self, conversation_id) -> ConversationModel | None
    async def list_conversations(self, skip, limit, project_id, status, search, user_id) -> list[ConversationModel]
    async def count_conversations(self, project_id, status, search, user_id) -> int
    async def update(self, conversation) -> ConversationModel
    async def delete(self, conversation_id) -> bool
    async def increment_message_count(self, conversation_id) -> None
```

### MessageRepositoryInterface

```python
class MessageRepositoryInterface(ABC):
    async def create(self, message) -> MessageModel
    async def get_by_id(self, message_id) -> MessageModel | None
    async def list_by_conversation(self, conversation_id, skip, limit) -> list[MessageModel]
    async def count_by_conversation(self, conversation_id) -> int
    async def delete(self, message_id) -> bool
```

## Use Cases

| Use Case | Input | Output | Validation |
|----------|-------|--------|------------|
| `CreateConversationUseCase` | title, user_id, ... | `ConversationModel` | Title required, ≤500 chars |
| `GetConversationUseCase` | conversation_id | `ConversationModel` | Raises `NotFoundException` if missing |
| `ListConversationsUseCase` | skip, limit, filters | `dict` (items, total, skip, limit) | Validates status enum |
| `UpdateConversationUseCase` | conversation_id, user_id, fields | `ConversationModel` | Creator-only, validates status |
| `DeleteConversationUseCase` | conversation_id, user_id | `bool` | Creator-only, cascades messages |
| `SendMessageUseCase` | conversation_id, content, user_id | `MessageModel` | Creator-only, active conversation, non-empty content |
| `ListMessagesUseCase` | conversation_id, skip, limit | `dict` (items, total, skip, limit) | Conversation must exist |
| `SummarizeLiteratureUseCase` | paper_ids, user_id, focus_areas | `dict` | At least one paper ID |
| `RecommendGenesUseCase` | trait_description, species | `dict` | Trait description required |
| `DesignExperimentUseCase` | research_question, user_id, ... | `dict` | Research question required |
| `AnalyzeImageUseCase` | image_url/image_base64, analysis_type | `dict` | Image required, valid analysis type |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/conversations` | Create conversation |
| GET | `/api/v1/ai/conversations` | List conversations (query: skip, limit, project_id, status_filter, search) |
| GET | `/api/v1/ai/conversations/{id}` | Get conversation |
| PUT | `/api/v1/ai/conversations/{id}` | Update conversation (creator only) |
| DELETE | `/api/v1/ai/conversations/{id}` | Delete conversation + cascade messages (creator only) |
| POST | `/api/v1/ai/conversations/{id}/messages` | Send message |
| GET | `/api/v1/ai/conversations/{id}/messages` | List messages (query: skip, limit) |
| POST | `/api/v1/ai/summarize-literature` | Summarize papers |
| POST | `/api/v1/ai/recommend-genes` | Gene recommendations |
| POST | `/api/v1/ai/design-experiment` | Experiment design |
| POST | `/api/v1/ai/analyze-image` | Image analysis |

## Validation Rules

- **Conversation title:** Required, non-empty, max 500 characters.
- **Status:** Must be `active`, `archived`, or `deleted`.
- **Message content:** Required, non-empty, max 50,000 characters.
- **Authorization:** Only the conversation creator can send messages, update, or delete.
- **Archived conversations:** Cannot receive new messages.
- **Literature summary:** At least one paper ID required.
- **Gene recommendation:** Trait description required, non-empty.
- **Experiment design:** Research question required, non-empty.
- **Image analysis:** Either `image_url` or `image_base64` required; `analysis_type` must be one of `general`, `phenotype`, `disease`, `growth_stage`, `morphism`.

## Example: Chat Conversation

```http
POST /api/v1/ai/conversations
Authorization: Bearer <token>

{
  "title": "Drought Tolerance Research",
  "description": "Exploring wheat drought tolerance mechanisms",
  "model_used": "gpt-4",
  "tags": ["drought", "wheat"]
}

# Response: { "id": "conv-uuid", "title": "Drought Tolerance Research", ... }
```

```http
POST /api/v1/ai/conversations/conv-uuid/messages
Authorization: Bearer <token>

{
  "content": "What are the key genes involved in wheat drought tolerance?"
}

# Response: { "role": "assistant", "content": "...", ... }
```

## Example: Gene Recommendation

```http
POST /api/v1/ai/recommend-genes
Authorization: Bearer <token>

{
  "trait_description": "drought tolerance during grain filling stage",
  "species": "Triticum aestivum"
}

# Response: { "recommendations": [], "trait": "...", "reasoning": "..." }
```

## Example: Experiment Design

```http
POST /api/v1/ai/design-experiment
Authorization: Bearer <token>

{
  "research_question": "How does nitrogen application rate affect wheat yield under water stress?",
  "species": "wheat",
  "variables": ["nitrogen_rate", "water_stress", "yield"],
  "constraints": {"field_size": "2 hectares", "season": "spring"}
}

# Response: { "experiment_design": {...}, "suggestions": [...] }
```

## AI Service Integration

The AI tools (summarize, recommend, design, analyze) are currently implemented as placeholder stubs. Production integration will connect to the separate `ai-service` container via HTTP, using LangGraph and LangChain agents. The `SendMessageUseCase` returns a placeholder response — production will call the AI service for real-time generation.

## Testing

```bash
cd apps/api
python -m pytest tests/unit/test_ai_assistant.py -v
```

56 unit tests covering:
- Interface contract validation
- All 11 use cases (success + error paths)
- 16 Pydantic schema validations
- 4 integration tests (module structure, router endpoints, class existence, repo exports)
