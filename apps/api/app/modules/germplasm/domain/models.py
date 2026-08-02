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


class SpeciesModel(Base):
    __tablename__ = "species"
    __table_args__ = {"schema": "germplasm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    common_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scientific_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    family: Mapped[str | None] = mapped_column(String(255), nullable=True)
    genus: Mapped[str | None] = mapped_column(String(255), nullable=True)
    species_epithet: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    accessions: Mapped[list["AccessionModel"]] = relationship(
        back_populates="species", cascade="all, delete-orphan"
    )


class AccessionModel(Base):
    __tablename__ = "accessions"
    __table_args__ = {"schema": "germplasm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    accession_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    species_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.species.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    collection_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    collection_date: Mapped[date | None] = mapped_column(nullable=True)
    collection_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    availability_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="available"
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

    species: Mapped["SpeciesModel"] = relationship(back_populates="accessions")
    passport_data: Mapped["PassportDataModel | None"] = relationship(
        back_populates="accession", uselist=False, cascade="all, delete-orphan"
    )
    pedigree: Mapped["PedigreeModel | None"] = relationship(
        back_populates="accession", uselist=False, cascade="all, delete-orphan",
        foreign_keys="[PedigreeModel.accession_id]"
    )
    seed_storages: Mapped[list["SeedStorageModel"]] = relationship(
        back_populates="accession", cascade="all, delete-orphan"
    )
    images: Mapped[list["GermplasmImageModel"]] = relationship(
        back_populates="accession", cascade="all, delete-orphan"
    )
    files: Mapped[list["GermplasmFileModel"]] = relationship(
        back_populates="accession", cascade="all, delete-orphan"
    )


class PassportDataModel(Base):
    __tablename__ = "passport_data"
    __table_args__ = {"schema": "germplasm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    accession_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.accessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    institute_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    institute_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    collection_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    collection_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    duplicates: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    accession: Mapped["AccessionModel"] = relationship(back_populates="passport_data")


class PedigreeModel(Base):
    __tablename__ = "pedigrees"
    __table_args__ = {"schema": "germplasm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    accession_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.accessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    parent1_accession_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.accessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    parent2_accession_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.accessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    parent1_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent2_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cross_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    generation: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    accession: Mapped["AccessionModel"] = relationship(
        back_populates="pedigree", foreign_keys=[accession_id]
    )


class SeedStorageModel(Base):
    __tablename__ = "seed_storages"
    __table_args__ = {"schema": "germplasm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    accession_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.accessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    container_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity_grams: Mapped[float | None] = mapped_column(Float, nullable=True)
    seed_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_conditions: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_date: Mapped[date | None] = mapped_column(nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(nullable=True)
    viability: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    accession: Mapped["AccessionModel"] = relationship(back_populates="seed_storages")


class GermplasmImageModel(Base):
    __tablename__ = "images"
    __table_args__ = {"schema": "germplasm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    accession_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.accessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    taken_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    accession: Mapped["AccessionModel"] = relationship(back_populates="images")


class GermplasmFileModel(Base):
    __tablename__ = "files"
    __table_args__ = {"schema": "germplasm"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    accession_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("germplasm.accessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    accession: Mapped["AccessionModel"] = relationship(back_populates="files")
