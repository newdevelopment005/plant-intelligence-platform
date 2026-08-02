# Genomics Module

## Overview

The Genomics module manages genomic sequences, variants, and gene annotations. It provides a comprehensive system for storing and querying genomic data including genome assemblies, variant calls, and gene annotations across multiple species.

## Features

- **Sequence Management**: Register and manage genome assemblies, exomes, transcriptomes, amplicons, and metagenomes
- **Variant Tracking**: Record and query genetic variants (SNP, indel, structural, CNV, MNV) with position, alleles, quality, and functional impact
- **Gene Annotations**: Store gene symbols, descriptions, GO terms, Pfam domains, KEGG pathways, and ortholog information
- **Variant Search**: Search variants by genomic region, type, gene, and quality
- **Bulk Import**: Bulk import large variant datasets

## Architecture

```
genomics/
├── domain/
│   ├── models.py          # 3 SQLAlchemy models
│   ├── interfaces.py      # 3 repository interfaces
│   └── use_cases.py       # 16 use cases
├── infrastructure/
│   ├── sequence_repository.py
│   ├── variant_repository.py
│   └── annotation_repository.py
├── api/
│   ├── router.py          # Full CRUD API
│   └── schemas.py         # Pydantic schemas
└── tasks.py               # Background tasks (placeholder)
```

## Domain Models

### SequenceModel
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Sequence name |
| description | TEXT | Description |
| sequence_type | VARCHAR(50) | genome, exome, transcriptome, amplicon, metagenome |
| species_id | UUID | FK to germplasm.species |
| project_id | UUID | FK to project.projects |
| accession_id | UUID | FK to germplasm.accessions |
| organism | VARCHAR(255) | Organism name |
| chromosome | VARCHAR(50) | Chromosome |
| start_position / end_position | BIGINT | Genomic coordinates |
| length | BIGINT | Sequence length |
| gc_content | DECIMAL | GC content (0-1) |
| assembly_level | VARCHAR(50) | Complete, scaffold, contig, etc. |
| genome_build | VARCHAR(50) | Reference genome version |

### VariantModel
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| sequence_id | UUID | FK to genomics.sequences |
| chromosome | VARCHAR(50) | Chromosome |
| position | BIGINT | Genomic position |
| reference_allele | TEXT | Reference allele(s) |
| alternate_allele | TEXT | Alternate allele(s) |
| variant_type | VARCHAR(50) | SNP, indel, structural, CNV, MNV |
| quality | DECIMAL | Variant quality score |
| depth | INT | Read depth |
| allele_frequency | DECIMAL | Allele frequency (0-1) |
| gene_name | VARCHAR(255) | Affected gene |
| impact | VARCHAR(50) | HIGH, MODERATE, LOW, MODIFIER |

### GeneAnnotationModel
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| sequence_id | UUID | FK to genomics.sequences |
| gene_symbol | VARCHAR(100) | Gene symbol |
| gene_name | VARCHAR(500) | Full gene name |
| description | TEXT | Gene description |
| chromosome | VARCHAR(50) | Chromosome |
| start_position / end_position | BIGINT | Gene coordinates |
| strand | VARCHAR(1) | + or - |
| biotype | VARCHAR(50) | protein_coding, lncRNA, etc. |
| go_terms | TEXT[] | Gene Ontology terms |
| pfam_domains | TEXT[] | Pfam protein domains |
| kegg_pathways | TEXT[] | KEGG pathway IDs |
| orthologs | JSONB | Cross-species orthologs |

## API Endpoints

### Sequences

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/sequences` | List sequences | Query: skip, limit, sequence_type, species_id, project_id, search |
| POST | `/sequences` | Register sequence | `{name, sequence_type, organism?, ...}` |
| GET | `/sequences/{id}` | Get sequence detail | - |
| PUT | `/sequences/{id}` | Update sequence | `{name?, organism?, ...}` |
| DELETE | `/sequences/{id}` | Delete sequence | - |

### Variants

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/sequences/{id}/variants` | List variants | Query: skip, limit, chromosome, variant_type, gene_name |
| POST | `/sequences/{id}/variants` | Add variant | `{chromosome, position, ref, alt, type, ...}` |
| POST | `/sequences/{id}/variants/bulk` | Bulk import | `{variants: [{...}, ...]}` |
| GET | `/variants/search` | Search variants | Query: sequence_id, chromosome, start, end, type, gene_name, min_quality |
| GET | `/variants/{id}` | Get variant detail | - |
| DELETE | `/variants/{id}` | Delete variant | - |

### Annotations

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/sequences/{id}/annotations` | List annotations | Query: skip, limit, search |
| POST | `/sequences/{id}/annotations` | Add annotation | `{gene_symbol, gene_name?, description?, go_terms?, ...}` |
| GET | `/annotations/{id}` | Get annotation detail | - |
| PUT | `/annotations/{id}` | Update annotation | `{gene_name?, go_terms?, ...}` |
| DELETE | `/annotations/{id}` | Delete annotation | - |

## Unit Tests

43 unit tests covering all use cases:
- Sequence CRUD (16 tests)
- Variant CRUD + Search + Bulk (15 tests)
- Annotation CRUD (12 tests)
