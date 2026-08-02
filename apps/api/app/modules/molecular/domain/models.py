import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
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


class MoleculeExperimentModel(Base):
    __tablename__ = "experiments"
    __table_args__ = {"schema": "molecular"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    experiment_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PCR"
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    species_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.species.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    protocol: Mapped[str | None] = mapped_column(Text, nullable=True)
    reagents: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    thermal_cycler_program: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="planned"
    )
    start_date: Mapped[date | None] = mapped_column(nullable=True)
    end_date: Mapped[date | None] = mapped_column(nullable=True)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    primers: Mapped[list["PrimerModel"]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )
    constructs: Mapped[list["ConstructModel"]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )


class PrimerModel(Base):
    __tablename__ = "primers"
    __table_args__ = {"schema": "molecular"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("molecular.experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sequence: Mapped[str] = mapped_column(Text, nullable=False)
    primer_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="forward"
    )
    target_gene: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_organism: Mapped[str | None] = mapped_column(String(255), nullable=True)
    length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tm: Mapped[float | None] = mapped_column(Float, nullable=True)
    gc_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    amplicon_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_validated: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    experiment: Mapped["MoleculeExperimentModel"] = relationship(back_populates="primers")


class ConstructModel(Base):
    __tablename__ = "constructs"
    __table_args__ = {"schema": "molecular"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("molecular.experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    construct_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="plasmid"
    )
    vector_backbone: Mapped[str | None] = mapped_column(String(255), nullable=True)
    insert_sequence: Mapped[str | None] = mapped_column(Text, nullable=True)
    insert_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    insert_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    selection_marker: Mapped[str | None] = mapped_column(String(255), nullable=True)
    promoter: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resistance: Mapped[str | None] = mapped_column(String(255), nullable=True)
    species_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.species.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_validated: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    experiment: Mapped["MoleculeExperimentModel"] = relationship(back_populates="constructs")
