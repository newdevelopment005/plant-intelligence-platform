# Architecture Documentation

## System Overview

The Plant Intelligence Platform follows a **Modular Monolith** architecture with **Microservice-Ready Boundaries**. This design provides the simplicity of a single deployable unit while maintaining clear domain separation that allows future extraction into microservices if needed.

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
│   Web App (Next.js)  |  Mobile (Future)  |  CLI  |  REST API    │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS
┌─────────────────────────────▼───────────────────────────────────┐
│                   REVERSE PROXY (Nginx)                          │
│          Rate Limiting  |  SSL/TLS  |  Routing  |  Caching      │
└────────┬────────────────────────────────────────────┬───────────┘
         │                                            │
┌────────▼──────────────────┐  ┌──────────────────────▼───────────┐
│       API SERVICE          │  │         AI SERVICE                │
│       (FastAPI)            │  │      (FastAPI + LangGraph)        │
│                           │  │                                   │
│  ┌─────────────────────┐  │  │  ┌─────────────────────────────┐  │
│  │   14 Domain Modules │  │  │  │   5 Specialist Agents       │  │
│  │   ─────────────────│  │  │  │   ──────────────────────── │  │
│  │   auth             │  │  │  │   Literature Agent          │  │
│  │   project          │  │  │  │   Gene Recommendation Agent │  │
│  │   germplasm        │  │  │  │   Experiment Design Agent   │  │
│  │   phenotyping      │  │  │  │   Image Analysis Agent      │  │
│  │   genomics         │  │  │  │   Data Integration Agent    │  │
│  │   molecular        │  │  │  └─────────────────────────────┘  │
│  │   literature       │  │  │                                   │
│  │   knowledge_graph  │  │  │  ┌─────────────────────────────┐  │
│  │   ai_assistant     │  │  │  │   Tool Layer                │  │
│  │   bioinformatics   │  │  │  │   PubMed, UniProt, BLAST    │  │
│  │   image_analysis   │  │  │  └─────────────────────────────┘  │
│  │   reporting        │  │  │                                   │
│  │   admin            │  │  │  ┌─────────────────────────────┐  │
│  │   lims             │  │  │  │   Embedding Pipeline        │  │
│  │   notebook         │  │  │  │   Sentence Transformers     │  │
│  └─────────────────────┘  │  │  └─────────────────────────────┘  │
│                           │  │                                   │
│  ┌─────────────────────┐  │  └───────────────────────────────────┘
│  │   Celery Workers    │  │
│  │   ─────────────────│  │
│  │   Default Queue    │  │
│  │   AI Queue         │  │
│  │   High Priority    │  │
│  │   Beat Scheduler   │  │
│  └─────────────────────┘  │
└────────┬──────────────────┘
         │
┌────────▼──────────────────────────────────────────────────────┐
│                       DATA LAYER                               │
│                                                                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│  │ PostgreSQL  │ │   Neo4j    │ │   Qdrant   │ │   Redis    │  │
│  │ ────────── │ │ ────────── │ │ ────────── │ │ ────────── │  │
│  │ Auth       │ │ Knowledge  │ │ Vector     │ │ Session    │  │
│  │ Projects   │ │ Graph      │ │ Embeddings │ │ Cache      │  │
│  │ Germplasm  │ │ Entities   │ │ Semantic   │ │ Task Queue │  │
│  │ Phenotype  │ │ Relations  │ │ Search     │ │ Rate Limit │  │
│  │ Genomics   │ │            │ │            │ │            │  │
│  │ Molecular  │ │            │ │            │ │            │  │
│  │ Literature │ │            │ │            │ │            │  │
│  │ Reports    │ │            │ │            │ │            │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. Modular Monolith
Strict domain boundaries within a single deployable unit. Each module encapsulates its own:
- Domain models and business rules
- Repository interfaces (ports)
- Use cases (application logic)
- API schemas and routes
- Database migrations (schema-per-module in PostgreSQL)

### 2. Clean Architecture
Business logic is independent of frameworks and databases:
- **Domain Layer**: Entities, value objects, repository interfaces
- **Application Layer**: Use cases orchestrate domain objects
- **Infrastructure Layer**: Database repositories, external API clients
- **Presentation Layer**: API routes, schemas, middleware

### 3. API-First Design
All features are accessible via REST APIs. The OpenAPI spec is auto-generated from code, ensuring documentation stays in sync.

### 4. Event-Driven Processing
Long-running tasks (AI inference, bulk imports, report generation) are handled asynchronously via Celery workers with Redis as the broker.

### 5. AI-Native Architecture
A dedicated AI service isolates resource-intensive ML workloads:
- Separate scaling (can run on GPU nodes)
- Independent deployment cycle
- Tool-based architecture for extensibility

## Module Structure

Each domain module follows a consistent structure:

```
modules/
└── <module>/
    ├── domain/
    │   ├── models.py          # Domain entities
    │   ├── interfaces.py      # Repository interfaces (ports)
    │   └── use_cases.py       # Application logic
    ├── infrastructure/
    │   └── repositories.py    # Database implementations
    ├── api/
    │   ├── router.py          # FastAPI routes
    │   └── schemas.py         # Pydantic request/response models
    └── tests/
        ├── unit/              # Use case tests (mocked)
        └── integration/       # Endpoint tests (httpx)
```

## Data Flow

### Request Lifecycle
```
Client → Nginx → FastAPI → Router → Use Case → Repository → Database
                                                         ↓
Client ← Nginx ← FastAPI ← Router ← Use Case ← Repository ← Response
```

### Async Task Flow
```
API Request → FastAPI → Celery Task (queued)
                              ↓
                    Celery Worker picks up task
                              ↓
                    Execute task (AI, import, report)
                              ↓
                    Store results in database
                              ↓
                    Optional: WebSocket notification
```

### AI Service Flow
```
API Request → AI Service Router → Agent Selection
                                       ↓
                              Agent executes tools
                                       ↓
                              Tool calls external API
                                       ↓
                              Agent processes results
                                       ↓
                              Return response to API
```

## Database Schema Design

### PostgreSQL (Schema-per-Module)
Each module owns its own schema, providing isolation while allowing cross-schema queries when needed:

| Schema | Purpose |
|--------|---------|
| `auth` | Users, roles, tokens |
| `project` | Projects, members |
| `germplasm` | Species, accessions, pedigree |
| `phenotyping` | Experiments, traits, measurements |
| `genomics` | Sequences, variants, annotations |
| `molecular` | Experiments, primers, constructs |
| `literature` | Papers, collections, notes |
| `knowledge_graph` | Entity/edge metadata |
| `ai_assistant` | Conversations, messages |
| `bioinformatics` | Analysis jobs, templates |
| `image_analysis` | Images, analysis jobs, results |
| `reporting` | Reports, templates |

### Neo4j (Knowledge Graph)
- **Nodes**: Scientific entities (genes, proteins, diseases, compounds)
- **Edges**: Relationships (REGULATES, INTERACTS_WITH, ASSOCIATED_WITH)
- **Properties**: Metadata on nodes and edges

### Qdrant (Vector Search)
- **Collections**: Paper embeddings, entity embeddings
- **Payloads**: Filterable metadata (year, source, entity_type)
- **Use**: Semantic search across literature and knowledge graph

## Technology Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Frontend | Next.js 15 App Router | Server Components, streaming, SEO |
| UI Components | shadcn/ui | Accessible, customizable, tree-shakeable |
| Styling | Tailwind CSS | Utility-first, rapid development |
| Backend | FastAPI | Async, type-safe, auto-docs |
| ORM | SQLAlchemy 2.0 | Mature, async support, Alembic |
| Migrations | Alembic | Schema versioning, autogenerate |
| Primary DB | PostgreSQL 16 | ACID, JSONB, full-text search |
| Graph DB | Neo4j 5 | O(1) graph traversals, Cypher |
| Vector DB | Qdrant | Purpose-built, payload filtering |
| Cache/Broker | Redis 7 | Sessions, queues, pub/sub |
| Task Queue | Celery | Mature, monitoring (Flower) |
| AI Framework | LangGraph | State machines, checkpointing |
| LLM | OpenAI GPT-4o | Reasoning, function calling |
| Embeddings | Sentence Transformers | Fast, CPU-friendly, local |
| HTTP Client | httpx | Async, testing support |
| Testing | pytest | Fixtures, markers, plugins |
| CI/CD | GitHub Actions | Native integration |
| Deployment | Docker + Vercel | Consistency + Next.js optimization |

## Security Architecture

```
┌─────────────────────────────────────────────┐
│                 SECURITY LAYERS              │
├─────────────────────────────────────────────┤
│ 1. Network    │ Nginx, Firewall, VPC        │
│ 2. Transport  │ TLS/HTTPS, Certificates     │
│ 3. Auth       │ JWT, Refresh Tokens, RBAC   │
│ 4. Application│ Input Validation, CORS      │
│ 5. Data       │ Encryption, Hashing         │
│ 6. Monitoring │ Logging, Alerting, Audit    │
└─────────────────────────────────────────────┘
```

## Scalability Considerations

| Dimension | Strategy |
|-----------|----------|
| Read | Redis cache, PostgreSQL read replicas |
| Write | Celery async processing, batch operations |
| Compute | Separate AI service (GPU scaling) |
| Storage | S3-compatible object storage (MinIO) |
| Horizontal | Stateless services, Docker scaling |

## Future Evolution

The architecture supports gradual migration to microservices:
1. Extract AI service (already separate)
2. Extract literature/knowledge graph (high coupling to external APIs)
3. Extract genomics/bioinformatics (compute-intensive)
4. Remainder as modular monolith
