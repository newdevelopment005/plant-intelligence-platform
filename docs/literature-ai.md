# Literature AI Repository

## Overview

The Literature AI module manages scientific papers, research collections, and reading notes. It provides paper CRUD with DOI/PMID deduplication, collection-based organization, annotation notes, and semantic search readiness for AI-powered literature discovery.

## Architecture

```
literature/
├── domain/
│   ├── models.py          # PaperModel, CollectionModel, NoteModel
│   ├── interfaces.py      # Repository interfaces (ABCs)
│   └── use_cases.py       # 19 use cases
├── infrastructure/
│   ├── paper_repository.py
│   ├── collection_repository.py
│   └── note_repository.py
└── api/
    ├── router.py          # 20 REST endpoints
    └── schemas.py         # Pydantic schemas
```

## Domain Models

### Paper
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| title | String(1000) | Paper title |
| abstract | Text | Full abstract |
| authors | ARRAY(String) | Author list |
| doi | String(255) | Digital Object Identifier (unique index) |
| pmid | String(50) | PubMed ID (unique index) |
| pmcid | String(50) | PubMed Central ID |
| journal | String(500) | Journal name |
| volume / issue / pages | String(50) | Bibliographic details |
| publication_date | Date | Publication date |
| year | Integer | Year (auto-computed) |
| source | String(50) | manual, pubmed, crossref, arxiv, biorxiv, doaj, import |
| paper_type | String(50) | article, review, meta_analysis, systematic_review, preprint, etc. |
| mesh_terms | ARRAY(String) | MeSH headings |
| keywords | ARRAY(String) | Author keywords |
| citations_count | Integer | Citation count |
| citation_dois | ARRAY(String) | Cited paper DOIs |
| summary | Text | AI-generated summary |
| embedding_id | String(255) | Vector store reference |
| tags | ARRAY(String) | User tags |
| project_id | UUID (FK) | Associated project |

### Collection
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | String(255) | Collection name |
| description | Text | Description |
| color | String(7) | Hex color code |
| project_id | UUID (FK) | Associated project |
| tags | ARRAY(String) | Tags |

### Note
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| paper_id | UUID (FK) | Parent paper |
| content | Text | Note content |
| page_number | Integer | Page reference |
| highlight_text | Text | Highlighted text |
| tags | ARRAY(String) | Tags |

## API Endpoints (20)

### Papers
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/literature/papers` | Create paper |
| GET | `/api/v1/literature/papers` | List papers (filterable by source, type, year) |
| GET | `/api/v1/literature/papers/{id}` | Get paper |
| PUT | `/api/v1/literature/papers/{id}` | Update paper |
| DELETE | `/api/v1/literature/papers/{id}` | Delete paper |

### Semantic Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/literature/search` | Semantic search via embeddings |

### Collections
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/literature/collections` | Create collection |
| GET | `/api/v1/literature/collections` | List collections |
| GET | `/api/v1/literature/collections/{id}` | Get collection |
| PUT | `/api/v1/literature/collections/{id}` | Update collection |
| DELETE | `/api/v1/literature/collections/{id}` | Delete collection |
| POST | `/api/v1/literature/collections/{id}/papers` | Add paper to collection |
| DELETE | `/api/v1/literature/collections/{id}/papers/{pid}` | Remove paper from collection |
| GET | `/api/v1/literature/collections/{id}/papers` | List papers in collection |

### Notes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/literature/papers/{id}/notes` | Create note |
| GET | `/api/v1/literature/papers/{id}/notes` | List notes for paper |
| GET | `/api/v1/literature/papers/{id}/notes/{nid}` | Get note |
| PUT | `/api/v1/literature/papers/{id}/notes/{nid}` | Update note |
| DELETE | `/api/v1/literature/papers/{id}/notes/{nid}` | Delete note |

## Use Cases (19)

| Use Case | Description |
|----------|-------------|
| CreatePaperUseCase | Create with DOI/PMID deduplication, source validation |
| GetPaperUseCase | Retrieve by ID |
| ListPapersUseCase | Paginated list with source/type/year/project filters |
| UpdatePaperUseCase | Update with creator-only permission |
| DeletePaperUseCase | Delete with creator-only permission |
| SearchPapersSemanticUseCase | Vector similarity search |
| CreateCollectionUseCase | Create named collection |
| GetCollectionUseCase | Retrieve by ID |
| ListCollectionsUseCase | Paginated list with project/search filters |
| UpdateCollectionUseCase | Update with creator-only permission |
| DeleteCollectionUseCase | Delete with creator-only permission |
| AddPaperToCollectionUseCase | Add paper with duplicate check |
| RemovePaperFromCollectionUseCase | Remove paper from collection |
| ListPapersInCollectionUseCase | List papers in a collection |
| CreateNoteUseCase | Create annotation on paper |
| GetNoteUseCase | Retrieve note by ID |
| ListNotesByPaperUseCase | List notes for a paper |
| UpdateNoteUseCase | Update with creator-only permission |
| DeleteNoteUseCase | Delete with creator-only permission |

## Validation Rules

- **Paper sources**: manual, pubmed, crossref, arxiv, biorxiv, doaj, import
- **Paper types**: article, review, meta_analysis, systematic_review, preprint, book_chapter, conference_paper, thesis, other
- **Duplicate detection**: DOI and PMID are checked for uniqueness
- **Authorization**: Only the creator can update/delete papers, collections, and notes

## Tests

63 unit tests covering:
- Repository interface contracts (3 tests)
- Paper use cases: CRUD + search + dedup (19 tests)
- Collection use cases: CRUD + paper management (13 tests)
- Note use cases: CRUD on paper annotations (10 tests)
- Schema validation (9 tests)
- Module structure integration (4 tests)
