# Germplasm Repository Module

## Overview

The Germplasm Repository module manages plant genetic resources including species, accessions, passport data, pedigrees, seed storage, images, and files. It provides a comprehensive system for genebanks and seed banks to track and manage their collections.

## Features

- **Species Management**: Register and catalog plant species with taxonomic information
- **Accession Tracking**: Manage individual germplasm accessions with unique identifiers
- **Passport Data**: Store international standard passport data (IPGRI format)
- **Pedigree Tracking**: Record parentage and breeding history with tree visualization
- **Seed Storage**: Track multiple storage locations with viability monitoring
- **Image Management**: Upload and organize germplasm photographs
- **File Attachments**: Store related documents (protocols, certificates, etc.)
- **Search & Filter**: Full-text search with species, status, and project filters
- **Geospatial Data**: Store collection location coordinates

## Architecture

```
germplasm/
├── domain/
│   ├── models.py          # 7 SQLAlchemy models
│   ├── interfaces.py      # 7 repository interfaces
│   └── use_cases.py       # 24 use cases
├── infrastructure/
│   ├── species_repository.py
│   ├── accession_repository.py
│   └── repositories.py    # Passport, Pedigree, Storage, Image, File repos
└── api/
    ├── router.py          # 30+ API endpoints
    └── schemas.py         # Pydantic request/response models
```

## Database Schema

### Species Table (`germplasm.species`)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| common_name | VARCHAR(255) | Common name |
| scientific_name | VARCHAR(255) | Binomial name (unique) |
| family | VARCHAR(255) | Taxonomic family |
| genus | VARCHAR(255) | Genus |
| species_epithet | VARCHAR(255) | Species epithet |
| description | TEXT | Optional description |

### Accessions Table (`germplasm.accessions`)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| accession_number | VARCHAR(100) | Unique identifier (e.g., PI 123456) |
| species_id | UUID | FK to species |
| project_id | UUID | FK to project (optional) |
| name | VARCHAR(255) | Descriptive name |
| description | TEXT | Optional description |
| collection_source | VARCHAR(255) | Where collected |
| collection_date | DATE | Collection date |
| collection_location | VARCHAR(255) | Location description |
| latitude | FLOAT | GPS latitude |
| longitude | FLOAT | GPS longitude |
| altitude | FLOAT | Elevation in meters |
| availability_status | ENUM | available, limited, unavailable, reserved |
| tags | TEXT[] | Searchable tags |
| metadata_json | JSONB | Flexible metadata |
| created_by | UUID | FK to auth.users |

### Passport Data Table (`germplasm.passport_data`)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| accession_id | UUID | FK to accessions (unique) |
| institute_code | VARCHAR(50) | FAO institute code |
| institute_name | VARCHAR(255) | Institute name |
| country_code | VARCHAR(10) | ISO country code |
| collection_number | VARCHAR(100) | Collector's number |
| collection_source | VARCHAR(255) | Source type |
| status | VARCHAR(50) | Availability status |
| duplicates | INT | Number of duplicates |

### Pedigree Table (`germplasm.pedigrees`)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| accession_id | UUID | FK to accessions (unique) |
| parent1_accession_id | UUID | FK to parent 1 |
| parent2_accession_id | UUID | FK to parent 2 |
| parent1_name | VARCHAR(255) | Parent 1 name |
| parent2_name | VARCHAR(255) | Parent 2 name |
| cross_type | VARCHAR(50) | Cross type |
| generation | INT | Breeding generation |

### Seed Storage Table (`germplasm.seed_storages`)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| accession_id | UUID | FK to accessions |
| location | VARCHAR(255) | Storage location |
| container_type | VARCHAR(50) | Container type |
| quantity_grams | FLOAT | Quantity in grams |
| seed_count | INT | Number of seeds |
| storage_conditions | VARCHAR(255) | Temperature, humidity |
| storage_date | DATE | When stored |
| expiry_date | DATE | Expiration date |
| viability | FLOAT | Germination rate % |

### Images Table (`germplasm.images`)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| accession_id | UUID | FK to accessions |
| filename | VARCHAR(255) | Stored filename |
| original_filename | VARCHAR(255) | Original filename |
| mime_type | VARCHAR(100) | MIME type |
| file_size | INT | Size in bytes |
| storage_path | VARCHAR(500) | File path |
| caption | TEXT | Image caption |
| image_type | VARCHAR(50) | Type (phenotype, flower, seed, etc.) |

### Files Table (`germplasm.files`)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| accession_id | UUID | FK to accessions |
| filename | VARCHAR(255) | Stored filename |
| original_filename | VARCHAR(255) | Original filename |
| mime_type | VARCHAR(100) | MIME type |
| file_size | INT | Size in bytes |
| storage_path | VARCHAR(500) | File path |
| description | TEXT | File description |
| file_type | VARCHAR(50) | Type (protocol, certificate, etc.) |

## API Endpoints

### Species

```
GET    /api/v1/germplasm/species              # List species
POST   /api/v1/germplasm/species              # Create species
GET    /api/v1/germplasm/species/{id}         # Get species
PUT    /api/v1/germplasm/species/{id}         # Update species
DELETE /api/v1/germplasm/species/{id}         # Delete species
```

### Accessions

```
GET    /api/v1/germplasm/accessions           # List accessions
POST   /api/v1/germplasm/accessions           # Create accession
GET    /api/v1/germplasm/accessions/search    # Search accessions
GET    /api/v1/germplasm/accessions/{id}      # Get accession
PUT    /api/v1/germplasm/accessions/{id}      # Update accession
DELETE /api/v1/germplasm/accessions/{id}      # Delete accession
```

### Passport Data

```
GET    /api/v1/germplasm/accessions/{id}/passport    # Get passport
POST   /api/v1/germplasm/accessions/{id}/passport    # Create passport
PUT    /api/v1/germplasm/accessions/{id}/passport    # Update passport
```

### Pedigree

```
GET    /api/v1/germplasm/accessions/{id}/pedigree      # Get pedigree
GET    /api/v1/germplasm/accessions/{id}/pedigree/tree # Get tree
POST   /api/v1/germplasm/accessions/{id}/pedigree      # Create pedigree
```

### Seed Storage

```
GET    /api/v1/germplasm/accessions/{id}/storage   # List storages
POST   /api/v1/germplasm/accessions/{id}/storage   # Add storage
PUT    /api/v1/germplasm/storage/{storage_id}      # Update storage
DELETE /api/v1/germplasm/storage/{storage_id}      # Delete storage
```

### Images & Files

```
GET    /api/v1/germplasm/accessions/{id}/images   # List images
POST   /api/v1/germplasm/accessions/{id}/images   # Upload image
DELETE /api/v1/germplasm/images/{image_id}         # Delete image
GET    /api/v1/germplasm/accessions/{id}/files    # List files
POST   /api/v1/germplasm/accessions/{id}/files    # Upload file
DELETE /api/v1/germplasm/files/{file_id}           # Delete file
```

## Frontend Pages

| Route | Description |
|-------|-------------|
| `/germplasm` | Species list and management |
| `/germplasm/accessions` | Accession list with filters |
| `/germplasm/accessions/[id]` | Accession detail with tabs |

## Tests

- **Unit tests**: `apps/api/tests/unit/test_germplasm.py` — 30+ test cases
- **Integration tests**: `apps/api/tests/integration/test_germplasm.py` — 15+ test cases

## Usage Example

```python
# Create a species
from app.modules.germplasm.domain.use_cases import CreateSpeciesUseCase

use_case = CreateSpeciesUseCase(species_repo)
species = await use_case.execute(
    common_name="Common wheat",
    scientific_name="Triticum aestivum",
    family="Poaceae"
)

# Create an accession
from app.modules.germplasm.domain.use_cases import CreateAccessionUseCase

use_case = CreateAccessionUseCase(accession_repo, species_repo)
accession = await use_case.execute(
    accession_number="PI 123456",
    species_id=str(species.id),
    name="Wheat landrace",
    latitude=27.7172,
    longitude=85.3240,
    user_id="user-123"
)

# Add seed storage
from app.modules.germplasm.domain.use_cases import CreateSeedStorageUseCase

use_case = CreateSeedStorageUseCase(storage_repo, accession_repo)
storage = await use_case.execute(
    accession_id=str(accession.id),
    location="Genebank Vault A",
    quantity_grams=100.5,
    storage_conditions="-18°C, 20% RH"
)
```
