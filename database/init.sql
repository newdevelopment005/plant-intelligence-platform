-- Plant Intelligence Platform - Database Initialization
-- This script runs on first PostgreSQL container start

-- Create schemas for module isolation
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS project;
CREATE SCHEMA IF NOT EXISTS germplasm;
CREATE SCHEMA IF NOT EXISTS phenotyping;
CREATE SCHEMA IF NOT EXISTS genomics;
CREATE SCHEMA IF NOT EXISTS molecular;
CREATE SCHEMA IF NOT EXISTS bioinformatics;
CREATE SCHEMA IF NOT EXISTS literature;
CREATE SCHEMA IF NOT EXISTS notebook;
CREATE SCHEMA IF NOT EXISTS lims;
CREATE SCHEMA IF NOT EXISTS reporting;
CREATE SCHEMA IF NOT EXISTS admin;
CREATE SCHEMA IF NOT EXISTS image_analysis;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable PostGIS for geospatial queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create custom types
DO $$ BEGIN
    CREATE TYPE auth.user_role AS ENUM ('admin', 'principal_investigator', 'researcher', 'technician', 'readonly');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE project.project_status AS ENUM ('active', 'archived', 'deleted');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE germplasm.availability_status AS ENUM ('available', 'limited', 'unavailable', 'reserved');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE phenotyping.experiment_type AS ENUM ('field', 'greenhouse', 'controlled_environment', 'growth_chamber');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE genomics.sequence_type AS ENUM ('genome', 'exome', 'transcriptome', 'amplicon', 'metagenome');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE genomics.variant_type AS ENUM ('SNP', 'indel', 'structural', 'CNV', 'MNV');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE notebook.entry_type AS ENUM ('protocol', 'observation', 'analysis', 'note', 'result');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE lims.sample_type AS ENUM ('DNA', 'RNA', 'protein', 'tissue', 'seed', 'leaf', 'root', 'flower', 'soil', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Grant permissions (development only)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA auth TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA project TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA germplasm TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA phenotyping TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA genomics TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA molecular TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA literature TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA notebook TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA lims TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA reporting TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA admin TO pip;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA image_analysis TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA auth TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA project TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA germplasm TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA phenotyping TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA genomics TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA molecular TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA literature TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA notebook TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA lims TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA reporting TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA admin TO pip;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA image_analysis TO pip;

-- Log completion
DO $$ BEGIN
    RAISE NOTICE 'Plant Intelligence Platform database initialized successfully';
END $$;
