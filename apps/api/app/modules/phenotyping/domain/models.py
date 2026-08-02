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


class ExperimentModel(Base):
    __tablename__ = "experiments"
    __table_args__ = {"schema": "phenotyping"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    experiment_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="field"
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_date: Mapped[date | None] = mapped_column(nullable=True)
    end_date: Mapped[date | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="planned"
    )
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

    traits: Mapped[list["TraitModel"]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )
    measurements: Mapped[list["MeasurementModel"]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )


class TraitModel(Base):
    __tablename__ = "traits"
    __table_args__ = {"schema": "phenotyping"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("phenotyping.experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    trait_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    data_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="numeric"
    )
    min_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    allowed_values: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    is_required: Mapped[bool] = mapped_column(default=False)
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

    experiment: Mapped["ExperimentModel"] = relationship(back_populates="traits")
    measurements: Mapped[list["MeasurementModel"]] = relationship(
        back_populates="trait", cascade="all, delete-orphan"
    )


class MeasurementModel(Base):
    __tablename__ = "measurements"
    __table_args__ = {"schema": "phenotyping"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("phenotyping.experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trait_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("phenotyping.traits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    accession_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.accessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    value_numeric: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    value_date: Mapped[date | None] = mapped_column(nullable=True)
    rep: Mapped[int | None] = mapped_column(Integer, nullable=True)
    block: Mapped[str | None] = mapped_column(String(50), nullable=True)
    plot: Mapped[str | None] = mapped_column(String(50), nullable=True)
    plant_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    measured_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    measured_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="SET NULL"),
        nullable=True,
    )
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
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

    experiment: Mapped["ExperimentModel"] = relationship(back_populates="measurements")
    trait: Mapped["TraitModel"] = relationship(back_populates="measurements")
