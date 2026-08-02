# Phenotyping Module

## Overview

The Phenotyping module manages plant phenotyping experiments, traits, and measurements. It provides a comprehensive system for recording, tracking, and analyzing phenotypic data across field trials, greenhouse experiments, and controlled environment studies.

## Features

- **Experiment Management**: Create and manage phenotyping experiments with location, dates, and metadata
- **Trait Definition**: Define phenotypic traits with data types, units, ranges, and allowed values
- **Measurement Recording**: Record individual measurements against traits and experiments
- **Bulk Import**: Bulk import large datasets of measurements
- **Experiment Summary**: Get statistical summaries (min, max, mean, count) per trait
- **Experiment Types**: Support for field, greenhouse, controlled environment, and growth chamber experiments

## Architecture

```
phenotyping/
├── domain/
│   ├── models.py          # 3 SQLAlchemy models
│   ├── interfaces.py      # 3 repository interfaces
│   └── use_cases.py       # 17 use cases
├── infrastructure/
│   ├── experiment_repository.py
│   ├── trait_repository.py
│   └── measurement_repository.py
├── api/
│   ├── router.py          # Full CRUD API
│   └── schemas.py         # Pydantic schemas
└── tasks.py               # Background tasks (placeholder)
```

## Domain Models

### ExperimentModel
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Experiment name |
| description | TEXT | Description |
| experiment_type | VARCHAR(50) | field, greenhouse, controlled_environment, growth_chamber |
| project_id | UUID | FK to projects |
| location | VARCHAR(255) | Physical location |
| latitude/longitude/altitude | DECIMAL | GPS coordinates |
| start_date / end_date | DATE | Duration |
| status | VARCHAR(50) | planned, in_progress, completed, archived |
| tags | TEXT[] | Categorization tags |
| created_by | UUID | FK to auth.users |

### TraitModel
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| experiment_id | UUID | FK to experiments |
| name | VARCHAR(255) | Trait name |
| description | TEXT | Description |
| trait_category | VARCHAR(100) | Category (morphological, physiological, etc.) |
| unit | VARCHAR(50) | Unit of measurement |
| data_type | VARCHAR(50) | numeric, text, categorical, date, boolean |
| min_value / max_value | DECIMAL | Valid range (for numeric) |
| allowed_values | TEXT[] | Allowed values (for categorical) |
| is_required | BOOLEAN | Required in experiments |

### MeasurementModel
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| experiment_id | UUID | FK to experiments |
| trait_id | UUID | FK to traits |
| accession_id | UUID | FK to germplasm.accessions |
| value_numeric | DECIMAL | Numeric value |
| value_text | VARCHAR(500) | Text value |
| value_date | DATE | Date value |
| rep / block / plot | VARCHAR/INT | Experimental design info |
| plant_id | VARCHAR(100) | Individual plant identifier |
| measured_at | TIMESTAMPTZ | When measured |
| measured_by | UUID | FK to auth.users |

## API Endpoints

### Experiments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/experiments` | List experiments with filters |
| POST | `/experiments` | Create experiment |
| GET | `/experiments/{id}` | Get experiment detail |
| PUT | `/experiments/{id}` | Update experiment |
| DELETE | `/experiments/{id}` | Delete experiment |
| GET | `/experiments/{id}/summary` | Get experiment statistics |

### Traits

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/experiments/{id}/traits` | List traits for experiment |
| POST | `/experiments/{id}/traits` | Create trait |
| GET | `/traits/{id}` | Get trait detail |
| PUT | `/traits/{id}` | Update trait |
| DELETE | `/traits/{id}` | Delete trait |

### Measurements

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/experiments/{id}/measurements` | List measurements |
| POST | `/experiments/{id}/measurements` | Add measurement |
| POST | `/experiments/{id}/measurements/bulk` | Bulk import measurements |
| GET | `/measurements/{id}` | Get measurement detail |
| PUT | `/measurements/{id}` | Update measurement |
| DELETE | `/measurements/{id}` | Delete measurement |

## Supported Traits

Based on scientific requirements, the module supports recording:

- Plant Height, Stem Diameter, Leaf Area, Leaf Number, Leaf Colour
- Canopy Cover, Root Length, Root Architecture
- Flowering Time, Maturity, Yield, Biomass, Harvest Index
- Disease Score, Stress Tolerance
- Seed Weight, Fruit Size, Fruit Quality
- Plant Architecture
- Time-Series Measurements

## Unit Tests

47 unit tests covering all use cases:
- Experiment CRUD (15 tests)
- Trait CRUD (14 tests)
- Measurement CRUD + Bulk (16 tests)
- Experiment Summary (1 test)
