# Changelog

All notable changes to the Plant Intelligence Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete platform implementation across 18 phases
- 14 functional modules with full CRUD operations
- 550+ unit tests, 60+ integration tests, 4 e2e tests
- Docker Compose production deployment configuration
- CI/CD pipelines (GitHub Actions)
- Comprehensive documentation (18 guides)

### Fixed
- Double-prefix bug in 7 router files (molecular, bioinformatics, literature, knowledge_graph, ai_assistant, image_analysis, reporting)

## [0.1.0] - 2026-08-02

### Added

#### Phase 1: Architecture & Repository Setup
- System architecture design (modular monolith)
- Technology stack selection (Next.js, FastAPI, PostgreSQL, Neo4j, Qdrant)
- Repository scaffolding with 160+ files
- Docker Compose with 5 databases
- CI/CD workflows (GitHub Actions)
- Database initialization schemas

#### Phase 2: Authentication & Authorization
- JWT authentication (access + refresh tokens)
- RBAC with 5 roles (admin, PI, researcher, technician, readonly)
- User registration, login, logout, password management
- 22 unit tests

#### Phase 3: Project Management
- Project CRUD with team management
- Role-based project access control
- Tag system and search/filtering
- Frontend pages (list, detail, settings)

#### Phase 4: Germplasm Repository
- 7 domain models (Species, Accession, Passport, Pedigree, SeedStorage, GermplasmImage, GermplasmFile)
- 24 use cases, 30+ API endpoints
- Passport data management (SMTA, DOI)
- Pedigree tree traversal
- Geospatial data support
- 100 unit tests

#### Phase 5: Phenotyping Repository
- 3 models (Experiment, Trait, Measurement)
- 17 use cases, 20+ endpoints
- Bulk measurement import
- Statistical summary generation
- 47 unit tests

#### Phase 6: Genomics Repository
- 3 models (Sequence, Variant, Annotation)
- 16 use cases, 20+ endpoints
- Variant search (region, type, gene)
- Bulk variant import
- 43 unit tests

#### Phase 7: Molecular Biology
- 3 models (MoleculeExperiment, Primer, Construct)
- 15 use cases, 18 schemas
- PCR, qPCR, RNA-Seq, CRISPR experiment types
- Primer design with GC content computation
- 62 unit tests

#### Phase 8: Literature AI
- 4 models (Paper, Collection, Note, PaperEmbedding)
- 19 use cases, 20+ endpoints
- DOI/PMID deduplication
- Semantic search readiness
- 63 unit tests

#### Phase 9: Knowledge Graph
- 2 models (Entity, Edge) on Neo4j
- 10 use cases, 11 endpoints
- Graph traversal with configurable depth
- Cross-module entity linking
- 36 unit tests

#### Phase 10: AI Research Assistant
- 2 models (Conversation, Message)
- 11 use cases, 11 endpoints
- Chat interface for research queries
- AI-powered literature summarization
- Gene recommendation engine
- 56 unit tests

#### Phase 11: Bioinformatics
- 2 models (AnalysisJob, PipelineTemplate)
- 11 use cases, 11 endpoints
- Pipeline template system
- Job lifecycle management (pending -> running -> completed/failed)
- 55 unit tests

#### Phase 12: Image Analysis
- 3 models (PlantImage, AnalysisJob, AnalysisResult)
- 9 use cases, 9 endpoints
- Disease detection, phenotype measurement, growth tracking
- 41 unit tests

#### Phase 13: Reporting
- 2 models (Report, ReportTemplate)
- 10 use cases, 10 endpoints
- Multi-format export
- Template-based report generation
- 47 unit tests

#### Phase 14: Deployment
- Docker Compose production overrides
- Deployment scripts (backup, restore, migrate)
- Nginx reverse proxy configuration
- Deployment documentation

#### Phase 15: Testing
- Shared test fixtures and factories (20 factory classes)
- Integration tests for all 12 modules
- End-to-end cross-module workflow tests
- Coverage configuration (70% minimum)

#### Phase 16: Documentation
- CHANGELOG.md (this file)
- SECURITY.md
- Enhanced architecture documentation
- 18 module-specific guides
- API reference (656 lines)
- Developer guide
