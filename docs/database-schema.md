# Database Schema Documentation

## Overview

The Plant Intelligence Platform uses three specialized databases:

1. **PostgreSQL**: Primary relational database for structured data
2. **Neo4j**: Graph database for knowledge relationships
3. **Qdrant**: Vector database for semantic search

## PostgreSQL Schemas

Each module has its own PostgreSQL schema for namespace isolation:

| Schema | Purpose |
|--------|---------|
| `auth` | Users, tokens, authentication |
| `project` | Research projects, membership |
| `germplasm` | Plant genetic resources |
| `phenotyping` | Experiments, traits, measurements |
| `genomics` | Sequences, variants, annotations |
| `molecular` | Experiments, primers, constructs |
| `literature` | Papers, collections, notes |
| `notebook` | ELN entries, versions, attachments |
| `lims` | Samples, equipment, reagents |
| `reporting` | Generated reports |
| `admin` | Audit logs, system config |

## Key Tables

### auth.users

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Unique email |
| hashed_password | VARCHAR(255) | bcrypt hash |
| full_name | VARCHAR(255) | Display name |
| role | VARCHAR(50) | RBAC role |
| orcid_id | VARCHAR(50) | ORCID researcher ID |

### germplasm.germplasm

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| accession_number | VARCHAR(100) | Unique identifier |
| species | VARCHAR(255) | Species name |
| latitude/longitude | DECIMAL | Collection site |
| breeding_type | VARCHAR(100) | landrace, elite, etc. |
| metadata | JSONB | Flexible attributes |

### genomics.variants

| Column | Type | Description |
|--------|------|-------------|
| chromosome | VARCHAR(50) | Chromosome |
| position | BIGINT | Genomic position |
| reference_allele | TEXT | Reference base(s) |
| alternate_allele | TEXT | Alternative base(s) |
| variant_type | VARCHAR(50) | SNP, indel, etc. |

## Neo4j Graph Schema

### Node Types

- `Species`: Plant species
- `Gene`: Genetic loci
- `Protein`: Protein products
- `Pathway`: Biological pathways
- `Trait`: Phenotypic traits
- `Paper`: Scientific publications

### Relationship Types

- `ENCODES`: Gene → Protein
- `PARTICIPATES_IN`: Gene → Pathway
- `REGULATES`: Gene → Gene
- `ASSOCIATED_WITH`: Gene → Trait
- `MENTIONS_GENE`: Paper → Gene
- `ORTHOLOG_OF`: Gene → Gene (cross-species)

## Qdrant Collections

| Collection | Vector Size | Purpose |
|------------|-------------|---------|
| literature_embeddings | 384 | Paper semantic search |
| image_embeddings | 512 | Phenotype image similarity |
| entity_embeddings | 384 | Knowledge graph entities |
| sequence_embeddings | 256 | Gene sequence similarity |
