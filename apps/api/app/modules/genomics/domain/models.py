import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SequenceModel(Base):
    __tablename__ = "sequences"
    __table_args__ = {"schema": "genomics"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sequence_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="genome"
    )
    species_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.species.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    accession_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.accessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    organism: Mapped[str | None] = mapped_column(String(255), nullable=True)
    strain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    chromosome: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_position: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    end_position: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    length: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    gc_content: Mapped[float | None] = mapped_column(Float, nullable=True)
    n50: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    scaffold_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assembly_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    genome_build: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    variants: Mapped[list["VariantModel"]] = relationship(
        back_populates="sequence", cascade="all, delete-orphan"
    )
    annotations: Mapped[list["GeneAnnotationModel"]] = relationship(
        back_populates="sequence", cascade="all, delete-orphan"
    )


class VariantModel(Base):
    __tablename__ = "variants"
    __table_args__ = {"schema": "genomics"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sequence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("genomics.sequences.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chromosome: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reference_allele: Mapped[str] = mapped_column(Text, nullable=False)
    alternate_allele: Mapped[str] = mapped_column(Text, nullable=False)
    variant_type: Mapped[str] = mapped_column(String(50), nullable=False)
    quality: Mapped[float | None] = mapped_column(Float, nullable=True)
    filter_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    depth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allele_frequency: Mapped[float | None] = mapped_column(Float, nullable=True)
    gene_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    impact: Mapped[str | None] = mapped_column(String(50), nullable=True)
    annotations: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    sequence: Mapped["SequenceModel"] = relationship(back_populates="variants")


class GeneAnnotationModel(Base):
    __tablename__ = "gene_annotations"
    __table_args__ = {"schema": "genomics"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sequence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("genomics.sequences.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gene_symbol: Mapped[str] = mapped_column(String(100), nullable=False)
    gene_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    chromosome: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_position: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    end_position: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    strand: Mapped[str | None] = mapped_column(String(1), nullable=True)
    biotype: Mapped[str | None] = mapped_column(String(50), nullable=True)
    go_terms: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    pfam_domains: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    kegg_pathways: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    orthologs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    expression_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    sequence: Mapped["SequenceModel"] = relationship(back_populates="annotations")
