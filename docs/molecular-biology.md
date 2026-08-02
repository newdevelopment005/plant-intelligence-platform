# Molecular Biology Repository

## Overview

The Molecular Biology Repository manages PCR, qPCR, RNA-Seq, CRISPR, and other molecular biology experiments. It provides full CRUD for experiments, primers, and constructs with automatic computation of primer GC content and length.

## Architecture

```
molecular/
├── domain/
│   ├── models.py          # MoleculeExperimentModel, PrimerModel, ConstructModel
│   ├── interfaces.py      # Repository interfaces (Abstract Base Classes)
│   └── use_cases.py       # 15 use cases: CRUD for experiments, primers, constructs
├── infrastructure/
│   ├── experiment_repository.py   # SQLAlchemy repository
│   ├── primer_repository.py       # SQLAlchemy repository
│   └── construct_repository.py    # SQLAlchemy repository
└── api/
    ├── router.py          # 15 REST endpoints
    └── schemas.py         # Pydantic request/response schemas
```

## Domain Models

### MoleculeExperiment
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | String(255) | Experiment name |
| description | Text | Optional description |
| experiment_type | String(50) | PCR, qPCR, RT-PCR, RNA-Seq, etc. |
| project_id | UUID (FK) | Associated project |
| species_id | UUID (FK) | Target species |
| protocol | Text | Experimental protocol |
| reagents | JSONB | Reagent details |
| thermal_cycler_program | JSONB | Thermocycler settings |
| status | String(50) | planned, in_progress, completed, archived |
| start_date | Date | Experiment start |
| end_date | Date | Experiment end |
| result_summary | Text | Results summary |
| notes | Text | Additional notes |
| tags | ARRAY(String) | Searchable tags |

### Primer
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| experiment_id | UUID (FK) | Parent experiment |
| name | String(255) | Primer name |
| sequence | Text | DNA sequence (A/T/C/G/N only) |
| primer_type | String(50) | forward, reverse, probe, nested, universal |
| target_gene | String(255) | Target gene name |
| target_organism | String(255) | Target organism |
| length | Integer | Auto-computed from sequence |
| tm | Float | Melting temperature |
| gc_percent | Float | Auto-computed GC content |
| amplicon_size | Integer | Expected amplicon size |
| is_validated | Boolean | Validation status |

### Construct
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| experiment_id | UUID (FK) | Parent experiment |
| name | String(255) | Construct name |
| construct_type | String(50) | plasmid, binary_vector, expression_construct, reporter, crispr_construct |
| vector_backbone | String(255) | Vector backbone name |
| insert_sequence | Text | Insert DNA sequence |
| insert_name | String(255) | Insert gene name |
| insert_size | Integer | Auto-computed from insert_sequence |
| selection_marker | String(255) | Selection marker |
| promoter | String(255) | Promoter |
| resistance | String(255) | Antibiotic resistance |
| is_validated | Boolean | Validation status |

## API Endpoints

### Experiments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/molecular/experiments` | Create experiment |
| GET | `/api/v1/molecular/experiments` | List experiments (filterable) |
| GET | `/api/v1/molecular/experiments/{id}` | Get experiment |
| PUT | `/api/v1/molecular/experiments/{id}` | Update experiment |
| DELETE | `/api/v1/molecular/experiments/{id}` | Delete experiment |

### Primers
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/molecular/experiments/{exp_id}/primers` | Create primer |
| GET | `/api/v1/molecular/experiments/{exp_id}/primers` | List primers |
| GET | `/api/v1/molecular/experiments/{exp_id}/primers/{id}` | Get primer |
| PUT | `/api/v1/molecular/experiments/{exp_id}/primers/{id}` | Update primer |
| DELETE | `/api/v1/molecular/experiments/{exp_id}/primers/{id}` | Delete primer |

### Constructs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/molecular/experiments/{exp_id}/constructs` | Create construct |
| GET | `/api/v1/molecular/experiments/{exp_id}/constructs` | List constructs |
| GET | `/api/v1/molecular/experiments/{exp_id}/constructs/{id}` | Get construct |
| PUT | `/api/v1/molecular/experiments/{exp_id}/constructs/{id}` | Update construct |
| DELETE | `/api/v1/molecular/experiments/{exp_id}/constructs/{id}` | Delete construct |

## Use Cases (15)

| Use Case | Description |
|----------|-------------|
| CreateMoleculeExperimentUseCase | Create with type validation, date validation |
| GetMoleculeExperimentUseCase | Retrieve by ID with NotFoundException |
| ListMoleculeExperimentsUseCase | Paginated list with type/status/project filters |
| UpdateMoleculeExperimentUseCase | Update with creator-only permission |
| DeleteMoleculeExperimentUseCase | Delete with creator-only permission |
| CreatePrimerUseCase | Create with experiment existence check, sequence validation (ATCGN) |
| GetPrimerUseCase | Retrieve by ID |
| ListPrimersUseCase | List by experiment with type/search filters |
| UpdatePrimerUseCase | Update with auto-recalculation of length/GC |
| DeletePrimerUseCase | Delete by ID |
| CreateConstructUseCase | Create with experiment existence check, type validation |
| GetConstructUseCase | Retrieve by ID |
| ListConstructsUseCase | List by experiment with type/search filters |
| UpdateConstructUseCase | Update with auto-recalculation of insert_size |
| DeleteConstructUseCase | Delete by ID |

## Validation Rules

- **Experiment types**: PCR, qPCR, RT-PCR, RNA-Seq, DNA_Extraction, RNA_Extraction, ChIP-Seq, ATAC-Seq, Proteomics, Metabolomics, CRISPR, Transformation, Cloning
- **Primer sequence**: Only A, T, C, G, N characters allowed
- **Primer types**: forward, reverse, probe, nested, universal
- **Construct types**: plasmid, binary_vector, expression_construct, reporter, crispr_construct
- **Authorization**: Only the creator can update/delete experiments
- **Auto-computed**: primer length, GC%, construct insert_size

## Tests

62 unit tests covering:
- Model validation rules (8 tests)
- Repository interface contracts (3 tests)
- Use case logic: success paths, not-found, validation errors, authorization (37 tests)
- Schema validation (10 tests)
- Module structure and integration (4 tests)
