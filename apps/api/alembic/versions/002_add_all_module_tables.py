"""add all module tables

Revision ID: 002
Revises: 001
Create Date: 2026-08-02 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS knowledge_graph")
    op.execute("CREATE SCHEMA IF NOT EXISTS ai_assistant")
    op.execute("CREATE SCHEMA IF NOT EXISTS image_analysis")
    op.execute("CREATE SCHEMA IF NOT EXISTS bioinformatics")

    # =============================================
    # PROJECT MODULE
    # =============================================
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="project",
    )

    op.create_table(
        "project_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="project",
    )

    # =============================================
    # GERMOPLASM MODULE
    # =============================================
    op.create_table(
        "species",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("common_name", sa.String(255), nullable=False),
        sa.Column("scientific_name", sa.String(255), nullable=False, unique=True),
        sa.Column("family", sa.String(255), nullable=True),
        sa.Column("genus", sa.String(255), nullable=True),
        sa.Column("species_epithet", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="germplasm",
    )

    op.create_table(
        "accessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("accession_number", sa.String(100), nullable=False, unique=True),
        sa.Column("species_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.species.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("collection_source", sa.String(255), nullable=True),
        sa.Column("collection_date", sa.Date, nullable=True),
        sa.Column("collection_location", sa.String(255), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("altitude", sa.Float, nullable=True),
        sa.Column("availability_status", sa.String(50), nullable=False, server_default="available"),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="germplasm",
    )

    op.create_table(
        "passport_data",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("accession_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.accessions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("institute_code", sa.String(50), nullable=True),
        sa.Column("institute_name", sa.String(255), nullable=True),
        sa.Column("country_code", sa.String(10), nullable=True),
        sa.Column("collection_number", sa.String(100), nullable=True),
        sa.Column("collection_source", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("duplicates", sa.Integer, nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="germplasm",
    )

    op.create_table(
        "pedigrees",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("accession_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.accessions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("parent1_accession_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.accessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("parent2_accession_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.accessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("parent1_name", sa.String(255), nullable=True),
        sa.Column("parent2_name", sa.String(255), nullable=True),
        sa.Column("cross_type", sa.String(50), nullable=True),
        sa.Column("generation", sa.Integer, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="germplasm",
    )

    op.create_table(
        "seed_storages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("accession_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.accessions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("container_type", sa.String(50), nullable=True),
        sa.Column("quantity_grams", sa.Float, nullable=True),
        sa.Column("seed_count", sa.Integer, nullable=True),
        sa.Column("storage_conditions", sa.String(255), nullable=True),
        sa.Column("storage_date", sa.Date, nullable=True),
        sa.Column("expiry_date", sa.Date, nullable=True),
        sa.Column("viability", sa.Float, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="germplasm",
    )

    op.create_table(
        "images",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("accession_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.accessions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.Integer, nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("thumbnail_path", sa.String(500), nullable=True),
        sa.Column("caption", sa.Text, nullable=True),
        sa.Column("image_type", sa.String(50), nullable=True),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("uploaded_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="germplasm",
    )

    op.create_table(
        "files",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("accession_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.accessions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.Integer, nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("file_type", sa.String(50), nullable=True),
        sa.Column("uploaded_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="germplasm",
    )

    # =============================================
    # PHENOTYPING MODULE
    # =============================================
    op.create_table(
        "experiments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("experiment_type", sa.String(50), nullable=False, server_default="field"),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("altitude", sa.Float, nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="planned"),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="phenotyping",
    )

    op.create_table(
        "traits",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("experiment_id", UUID(as_uuid=True), sa.ForeignKey("phenotyping.experiments.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("trait_category", sa.String(100), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("data_type", sa.String(50), nullable=False, server_default="numeric"),
        sa.Column("min_value", sa.Float, nullable=True),
        sa.Column("max_value", sa.Float, nullable=True),
        sa.Column("allowed_values", ARRAY(sa.String), nullable=True),
        sa.Column("is_required", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="phenotyping",
    )

    op.create_table(
        "measurements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("experiment_id", UUID(as_uuid=True), sa.ForeignKey("phenotyping.experiments.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("trait_id", UUID(as_uuid=True), sa.ForeignKey("phenotyping.traits.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("accession_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.accessions.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("value_numeric", sa.Float, nullable=True),
        sa.Column("value_text", sa.String(500), nullable=True),
        sa.Column("value_date", sa.Date, nullable=True),
        sa.Column("rep", sa.Integer, nullable=True),
        sa.Column("block", sa.String(50), nullable=True),
        sa.Column("plot", sa.String(50), nullable=True),
        sa.Column("plant_id", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("measured_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="phenotyping",
    )

    # =============================================
    # GENOMICS MODULE
    # =============================================
    op.create_table(
        "sequences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("sequence_type", sa.String(50), nullable=False, server_default="genome"),
        sa.Column("species_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.species.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("accession_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.accessions.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("organism", sa.String(255), nullable=True),
        sa.Column("strain", sa.String(255), nullable=True),
        sa.Column("chromosome", sa.String(50), nullable=True),
        sa.Column("start_position", sa.BigInteger, nullable=True),
        sa.Column("end_position", sa.BigInteger, nullable=True),
        sa.Column("length", sa.BigInteger, nullable=True),
        sa.Column("gc_content", sa.Float, nullable=True),
        sa.Column("n50", sa.BigInteger, nullable=True),
        sa.Column("scaffold_count", sa.Integer, nullable=True),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("assembly_level", sa.String(50), nullable=True),
        sa.Column("genome_build", sa.String(50), nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="genomics",
    )

    op.create_table(
        "variants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sequence_id", UUID(as_uuid=True), sa.ForeignKey("genomics.sequences.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("chromosome", sa.String(50), nullable=False),
        sa.Column("position", sa.BigInteger, nullable=False),
        sa.Column("reference_allele", sa.Text, nullable=False),
        sa.Column("alternate_allele", sa.Text, nullable=False),
        sa.Column("variant_type", sa.String(50), nullable=False),
        sa.Column("quality", sa.Float, nullable=True),
        sa.Column("filter_status", sa.String(50), nullable=True),
        sa.Column("depth", sa.Integer, nullable=True),
        sa.Column("allele_frequency", sa.Float, nullable=True),
        sa.Column("gene_name", sa.String(255), nullable=True),
        sa.Column("impact", sa.String(50), nullable=True),
        sa.Column("annotations", JSONB, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="genomics",
    )

    op.create_table(
        "gene_annotations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sequence_id", UUID(as_uuid=True), sa.ForeignKey("genomics.sequences.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("gene_symbol", sa.String(100), nullable=False),
        sa.Column("gene_name", sa.String(500), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("chromosome", sa.String(50), nullable=True),
        sa.Column("start_position", sa.BigInteger, nullable=True),
        sa.Column("end_position", sa.BigInteger, nullable=True),
        sa.Column("strand", sa.String(1), nullable=True),
        sa.Column("biotype", sa.String(50), nullable=True),
        sa.Column("go_terms", ARRAY(sa.String), nullable=True),
        sa.Column("pfam_domains", ARRAY(sa.String), nullable=True),
        sa.Column("kegg_pathways", ARRAY(sa.String), nullable=True),
        sa.Column("orthologs", JSONB, nullable=True),
        sa.Column("expression_data", JSONB, nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="genomics",
    )

    # =============================================
    # MOLECULAR MODULE
    # =============================================
    op.create_table(
        "experiments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("experiment_type", sa.String(50), nullable=False, server_default="PCR"),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("species_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.species.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("protocol", sa.Text, nullable=True),
        sa.Column("reagents", JSONB, nullable=True),
        sa.Column("thermal_cycler_program", JSONB, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="planned"),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("result_summary", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="molecular",
    )

    op.create_table(
        "primers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("experiment_id", UUID(as_uuid=True), sa.ForeignKey("molecular.experiments.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("sequence", sa.Text, nullable=False),
        sa.Column("primer_type", sa.String(50), nullable=False, server_default="forward"),
        sa.Column("target_gene", sa.String(255), nullable=True),
        sa.Column("target_organism", sa.String(255), nullable=True),
        sa.Column("length", sa.Integer, nullable=True),
        sa.Column("tm", sa.Float, nullable=True),
        sa.Column("gc_percent", sa.Float, nullable=True),
        sa.Column("amplicon_size", sa.Integer, nullable=True),
        sa.Column("is_validated", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="molecular",
    )

    op.create_table(
        "constructs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("experiment_id", UUID(as_uuid=True), sa.ForeignKey("molecular.experiments.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("construct_type", sa.String(50), nullable=False, server_default="plasmid"),
        sa.Column("vector_backbone", sa.String(255), nullable=True),
        sa.Column("insert_sequence", sa.Text, nullable=True),
        sa.Column("insert_name", sa.String(255), nullable=True),
        sa.Column("insert_size", sa.Integer, nullable=True),
        sa.Column("total_size", sa.Integer, nullable=True),
        sa.Column("selection_marker", sa.String(255), nullable=True),
        sa.Column("promoter", sa.String(255), nullable=True),
        sa.Column("resistance", sa.String(255), nullable=True),
        sa.Column("species_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.species.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("is_validated", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="molecular",
    )

    # =============================================
    # BIOINFORMATICS MODULE
    # =============================================
    op.create_table(
        "analysis_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("analysis_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("input_data", JSONB, nullable=True),
        sa.Column("parameters", JSONB, nullable=True),
        sa.Column("result_data", JSONB, nullable=True),
        sa.Column("output_files", ARRAY(sa.String), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("progress_percent", sa.Integer, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("runtime_seconds", sa.Float, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="bioinformatics",
    )

    op.create_table(
        "pipeline_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("analysis_type", sa.String(50), nullable=False),
        sa.Column("steps", JSONB, nullable=True),
        sa.Column("default_parameters", JSONB, nullable=True),
        sa.Column("required_inputs", ARRAY(sa.String), nullable=True),
        sa.Column("version", sa.String(20), nullable=False, server_default="1.0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="bioinformatics",
    )

    # =============================================
    # LITERATURE MODULE
    # =============================================
    op.create_table(
        "papers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("abstract", sa.Text, nullable=True),
        sa.Column("authors", ARRAY(sa.String), nullable=True),
        sa.Column("doi", sa.String(255), nullable=True, index=True),
        sa.Column("pmid", sa.String(50), nullable=True, index=True),
        sa.Column("pmcid", sa.String(50), nullable=True),
        sa.Column("journal", sa.String(500), nullable=True),
        sa.Column("journal_abbrev", sa.String(255), nullable=True),
        sa.Column("volume", sa.String(50), nullable=True),
        sa.Column("issue", sa.String(50), nullable=True),
        sa.Column("pages", sa.String(50), nullable=True),
        sa.Column("publication_date", sa.Date, nullable=True),
        sa.Column("year", sa.Integer, nullable=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("source_url", sa.String(2000), nullable=True),
        sa.Column("pdf_url", sa.String(2000), nullable=True),
        sa.Column("mesh_terms", ARRAY(sa.String), nullable=True),
        sa.Column("keywords", ARRAY(sa.String), nullable=True),
        sa.Column("language", sa.String(10), nullable=True),
        sa.Column("paper_type", sa.String(50), nullable=False, server_default="article"),
        sa.Column("is_open_access", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("citations_count", sa.Integer, nullable=True),
        sa.Column("citation_dois", ARRAY(sa.String), nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("embedding_id", sa.String(255), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="literature",
    )

    op.create_table(
        "collections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="literature",
    )

    op.create_table(
        "collection_papers",
        sa.Column("collection_id", UUID(as_uuid=True), sa.ForeignKey("literature.collections.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("paper_id", UUID(as_uuid=True), sa.ForeignKey("literature.papers.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="literature",
    )

    op.create_table(
        "notes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("paper_id", UUID(as_uuid=True), sa.ForeignKey("literature.papers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("page_number", sa.Integer, nullable=True),
        sa.Column("highlight_text", sa.Text, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="literature",
    )

    # =============================================
    # KNOWLEDGE GRAPH MODULE
    # =============================================
    op.create_table(
        "entities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source_module", sa.String(100), nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("properties", JSONB, nullable=True),
        sa.Column("tags", JSONB, nullable=True),
        sa.Column("embedding_id", sa.String(255), nullable=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="knowledge_graph",
    )

    op.create_table(
        "edges",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_entity_id", UUID(as_uuid=True), sa.ForeignKey("knowledge_graph.entities.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("target_entity_id", UUID(as_uuid=True), sa.ForeignKey("knowledge_graph.entities.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("relation_type", sa.String(200), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("properties", JSONB, nullable=True),
        sa.Column("weight", sa.Float, nullable=True),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="knowledge_graph",
    )

    # =============================================
    # AI ASSISTANT MODULE
    # =============================================
    op.create_table(
        "conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("message_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="ai_assistant",
    )

    op.create_table(
        "messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("ai_assistant.conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("tokens_used", sa.Integer, nullable=True),
        sa.Column("sources", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("metadata_json", JSONB, nullable=True),
        schema="ai_assistant",
    )

    # =============================================
    # IMAGE ANALYSIS MODULE
    # =============================================
    op.create_table(
        "plant_images",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("file_url", sa.String(2000), nullable=False),
        sa.Column("thumbnail_url", sa.String(2000), nullable=True),
        sa.Column("file_size_bytes", sa.Integer, nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("width", sa.Integer, nullable=True),
        sa.Column("height", sa.Integer, nullable=True),
        sa.Column("image_type", sa.String(50), nullable=False, server_default="general"),
        sa.Column("source_module", sa.String(50), nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("species", sa.String(255), nullable=True),
        sa.Column("tissue_type", sa.String(100), nullable=True),
        sa.Column("growth_stage", sa.String(100), nullable=True),
        sa.Column("magnification", sa.String(50), nullable=True),
        sa.Column("capture_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("gps_latitude", sa.Float, nullable=True),
        sa.Column("gps_longitude", sa.Float, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="image_analysis",
    )

    op.create_table(
        "analysis_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("image_id", UUID(as_uuid=True), sa.ForeignKey("image_analysis.plant_images.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("analysis_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("parameters", JSONB, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("runtime_seconds", sa.Float, nullable=True),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="image_analysis",
    )

    op.create_table(
        "analysis_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("job_id", UUID(as_uuid=True), sa.ForeignKey("image_analysis.analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("result_type", sa.String(50), nullable=False),
        sa.Column("label", sa.String(255), nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("bbox", JSONB, nullable=True),
        sa.Column("measurements", JSONB, nullable=True),
        sa.Column("annotations", JSONB, nullable=True),
        sa.Column("raw_output", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="image_analysis",
    )

    # =============================================
    # REPORTING MODULE
    # =============================================
    op.create_table(
        "reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("format", sa.String(20), nullable=False, server_default="pdf"),
        sa.Column("data_source", sa.String(100), nullable=True),
        sa.Column("parameters", JSONB, nullable=True),
        sa.Column("file_url", sa.String(2000), nullable=True),
        sa.Column("file_size_bytes", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="reporting",
    )

    op.create_table(
        "report_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("default_format", sa.String(20), nullable=False, server_default="pdf"),
        sa.Column("data_source", sa.String(100), nullable=True),
        sa.Column("layout", JSONB, nullable=True),
        sa.Column("default_parameters", JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="reporting",
    )

    # =============================================
    # NOTEBOOK MODULE
    # =============================================
    op.create_table(
        "entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("entry_type", sa.String(50), nullable=False, server_default="note"),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("is_locked", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="notebook",
    )

    op.create_table(
        "versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entry_id", UUID(as_uuid=True), sa.ForeignKey("notebook.entries.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="notebook",
    )

    # =============================================
    # LIMS MODULE
    # =============================================
    op.create_table(
        "samples",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sample_code", sa.String(100), nullable=False, unique=True),
        sa.Column("sample_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("parent_sample_id", UUID(as_uuid=True), sa.ForeignKey("lims.samples.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("project.projects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("accession_id", UUID(as_uuid=True), sa.ForeignKey("germplasm.accessions.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("quantity", sa.Float, nullable=True),
        sa.Column("unit", sa.String(20), nullable=True),
        sa.Column("storage_temp", sa.String(50), nullable=True),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="lims",
    )

    op.create_table(
        "sample_transfers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sample_id", UUID(as_uuid=True), sa.ForeignKey("lims.samples.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("from_location", sa.String(255), nullable=False),
        sa.Column("to_location", sa.String(255), nullable=False),
        sa.Column("quantity_transferred", sa.Float, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("transferred_by", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("transferred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="lims",
    )

    op.create_table(
        "equipment",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("equipment_code", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="available"),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("model_number", sa.String(255), nullable=True),
        sa.Column("serial_number", sa.String(255), nullable=True),
        sa.Column("last_calibration", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_calibration", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="lims",
    )

    op.create_table(
        "reagents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("catalog_number", sa.String(100), nullable=True),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("quantity", sa.Float, nullable=False, server_default=sa.text("0")),
        sa.Column("unit", sa.String(20), nullable=False, server_default="'mL'"),
        sa.Column("min_quantity", sa.Float, nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("storage_conditions", sa.String(255), nullable=True),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lot_number", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="lims",
    )


def downgrade() -> None:
    op.drop_table("reagents", schema="lims")
    op.drop_table("equipment", schema="lims")
    op.drop_table("sample_transfers", schema="lims")
    op.drop_table("samples", schema="lims")
    op.drop_table("versions", schema="notebook")
    op.drop_table("entries", schema="notebook")
    op.drop_table("report_templates", schema="reporting")
    op.drop_table("reports", schema="reporting")
    op.drop_table("analysis_results", schema="image_analysis")
    op.drop_table("analysis_jobs", schema="image_analysis")
    op.drop_table("plant_images", schema="image_analysis")
    op.drop_table("messages", schema="ai_assistant")
    op.drop_table("conversations", schema="ai_assistant")
    op.drop_table("edges", schema="knowledge_graph")
    op.drop_table("entities", schema="knowledge_graph")
    op.drop_table("notes", schema="literature")
    op.drop_table("collection_papers", schema="literature")
    op.drop_table("collections", schema="literature")
    op.drop_table("papers", schema="literature")
    op.drop_table("pipeline_templates", schema="bioinformatics")
    op.drop_table("analysis_jobs", schema="bioinformatics")
    op.drop_table("constructs", schema="molecular")
    op.drop_table("primers", schema="molecular")
    op.drop_table("experiments", schema="molecular")
    op.drop_table("gene_annotations", schema="genomics")
    op.drop_table("variants", schema="genomics")
    op.drop_table("sequences", schema="genomics")
    op.drop_table("measurements", schema="phenotyping")
    op.drop_table("traits", schema="phenotyping")
    op.drop_table("experiments", schema="phenotyping")
    op.drop_table("files", schema="germplasm")
    op.drop_table("images", schema="germplasm")
    op.drop_table("seed_storages", schema="germplasm")
    op.drop_table("pedigrees", schema="germplasm")
    op.drop_table("passport_data", schema="germplasm")
    op.drop_table("accessions", schema="germplasm")
    op.drop_table("species", schema="germplasm")
    op.drop_table("project_members", schema="project")
    op.drop_table("projects", schema="project")
