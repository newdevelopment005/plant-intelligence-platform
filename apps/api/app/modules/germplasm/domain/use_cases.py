from datetime import UTC, datetime

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.germplasm.domain.interfaces import (
    AccessionRepositoryInterface,
    GermplasmFileRepositoryInterface,
    GermplasmImageRepositoryInterface,
    PassportDataRepositoryInterface,
    PedigreeRepositoryInterface,
    SeedStorageRepositoryInterface,
    SpeciesRepositoryInterface,
)
from app.modules.germplasm.domain.models import (
    AccessionModel,
    GermplasmFileModel,
    GermplasmImageModel,
    PassportDataModel,
    PedigreeModel,
    SeedStorageModel,
    SpeciesModel,
)


class CreateSpeciesUseCase:
    def __init__(self, species_repo: SpeciesRepositoryInterface):
        self.species_repo = species_repo

    async def execute(
        self,
        common_name: str,
        scientific_name: str,
        family: str | None = None,
        genus: str | None = None,
        species_epithet: str | None = None,
        description: str | None = None,
    ) -> SpeciesModel:
        self._validate_name(common_name, "Common name")
        self._validate_name(scientific_name, "Scientific name")

        existing = await self.species_repo.get_by_scientific_name(scientific_name)
        if existing:
            raise ConflictException(f"Species with scientific name '{scientific_name}' already exists")

        species = SpeciesModel(
            common_name=common_name.strip(),
            scientific_name=scientific_name.strip(),
            family=family.strip() if family else None,
            genus=genus.strip() if genus else None,
            species_epithet=species_epithet.strip() if species_epithet else None,
            description=description.strip() if description else None,
            created_at=datetime.now(UTC),
        )

        return await self.species_repo.create(species)

    def _validate_name(self, name: str, field_name: str) -> None:
        if not name or not name.strip():
            raise ValidationException(f"{field_name} is required")
        if len(name.strip()) > 255:
            raise ValidationException(f"{field_name} must be less than 255 characters")


class GetSpeciesUseCase:
    def __init__(self, species_repo: SpeciesRepositoryInterface):
        self.species_repo = species_repo

    async def execute(self, species_id: str) -> SpeciesModel:
        species = await self.species_repo.get_by_id(species_id)
        if not species:
            raise NotFoundException("Species", species_id)
        return species


class ListSpeciesUseCase:
    def __init__(self, species_repo: SpeciesRepositoryInterface):
        self.species_repo = species_repo

    async def execute(
        self, skip: int = 0, limit: int = 20, search: str | None = None
    ) -> dict:
        species = await self.species_repo.list_species(skip=skip, limit=limit, search=search)
        total = await self.species_repo.count_species(search=search)

        return {
            "items": [
                {
                    "id": str(s.id),
                    "common_name": s.common_name,
                    "scientific_name": s.scientific_name,
                    "family": s.family,
                    "genus": s.genus,
                    "species_epithet": s.species_epithet,
                    "created_at": s.created_at.isoformat(),
                }
                for s in species
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateSpeciesUseCase:
    def __init__(self, species_repo: SpeciesRepositoryInterface):
        self.species_repo = species_repo

    async def execute(
        self,
        species_id: str,
        common_name: str | None = None,
        scientific_name: str | None = None,
        family: str | None = None,
        genus: str | None = None,
        species_epithet: str | None = None,
        description: str | None = None,
    ) -> SpeciesModel:
        species = await self.species_repo.get_by_id(species_id)
        if not species:
            raise NotFoundException("Species", species_id)

        if common_name is not None:
            if not common_name.strip():
                raise ValidationException("Common name cannot be empty")
            species.common_name = common_name.strip()

        if scientific_name is not None:
            if not scientific_name.strip():
                raise ValidationException("Scientific name cannot be empty")
            existing = await self.species_repo.get_by_scientific_name(scientific_name)
            if existing and str(existing.id) != species_id:
                raise ConflictException(f"Species with scientific name '{scientific_name}' already exists")
            species.scientific_name = scientific_name.strip()

        if family is not None:
            species.family = family.strip() if family else None
        if genus is not None:
            species.genus = genus.strip() if genus else None
        if species_epithet is not None:
            species.species_epithet = species_epithet.strip() if species_epithet else None
        if description is not None:
            species.description = description.strip() if description else None

        return await self.species_repo.update(species)


class DeleteSpeciesUseCase:
    def __init__(self, species_repo: SpeciesRepositoryInterface):
        self.species_repo = species_repo

    async def execute(self, species_id: str) -> bool:
        species = await self.species_repo.get_by_id(species_id)
        if not species:
            raise NotFoundException("Species", species_id)

        return await self.species_repo.delete(species_id)


class CreateAccessionUseCase:
    def __init__(
        self,
        accession_repo: AccessionRepositoryInterface,
        species_repo: SpeciesRepositoryInterface,
    ):
        self.accession_repo = accession_repo
        self.species_repo = species_repo

    async def execute(
        self,
        accession_number: str,
        species_id: str,
        name: str,
        project_id: str | None = None,
        description: str | None = None,
        collection_source: str | None = None,
        collection_date: str | None = None,
        collection_location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        altitude: float | None = None,
        tags: list[str] | None = None,
        user_id: str | None = None,
    ) -> AccessionModel:
        if not accession_number or not accession_number.strip():
            raise ValidationException("Accession number is required")
        if len(accession_number.strip()) > 100:
            raise ValidationException("Accession number must be less than 100 characters")
        if not name or not name.strip():
            raise ValidationException("Accession name is required")

        species = await self.species_repo.get_by_id(species_id)
        if not species:
            raise NotFoundException("Species", species_id)

        existing = await self.accession_repo.get_by_accession_number(accession_number)
        if existing:
            raise ConflictException(f"Accession with number '{accession_number}' already exists")

        accession = AccessionModel(
            accession_number=accession_number.strip(),
            species_id=species_id,
            project_id=project_id,
            name=name.strip(),
            description=description.strip() if description else None,
            collection_source=collection_source.strip() if collection_source else None,
            collection_date=collection_date,
            collection_location=collection_location.strip() if collection_location else None,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            availability_status="available",
            tags=tags,
            created_by=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.accession_repo.create(accession)


class GetAccessionUseCase:
    def __init__(self, accession_repo: AccessionRepositoryInterface):
        self.accession_repo = accession_repo

    async def execute(self, accession_id: str) -> AccessionModel:
        accession = await self.accession_repo.get_by_id(accession_id)
        if not accession:
            raise NotFoundException("Accession", accession_id)
        return accession


class ListAccessionsUseCase:
    def __init__(self, accession_repo: AccessionRepositoryInterface):
        self.accession_repo = accession_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        species_id: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        accessions = await self.accession_repo.list_accessions(
            skip=skip,
            limit=limit,
            species_id=species_id,
            project_id=project_id,
            status=status,
            search=search,
            user_id=user_id,
        )
        total = await self.accession_repo.count_accessions(
            species_id=species_id,
            project_id=project_id,
            status=status,
            search=search,
            user_id=user_id,
        )

        return {
            "items": [
                {
                    "id": str(a.id),
                    "accession_number": a.accession_number,
                    "name": a.name,
                    "species_id": str(a.species_id),
                    "project_id": str(a.project_id) if a.project_id else None,
                    "description": a.description,
                    "availability_status": a.availability_status,
                    "latitude": a.latitude,
                    "longitude": a.longitude,
                    "tags": a.tags,
                    "created_at": a.created_at.isoformat(),
                    "updated_at": a.updated_at.isoformat(),
                }
                for a in accessions
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


class UpdateAccessionUseCase:
    def __init__(self, accession_repo: AccessionRepositoryInterface):
        self.accession_repo = accession_repo

    async def execute(
        self,
        accession_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        collection_source: str | None = None,
        availability_status: str | None = None,
        tags: list[str] | None = None,
    ) -> AccessionModel:
        accession = await self.accession_repo.get_by_id(accession_id)
        if not accession:
            raise NotFoundException("Accession", accession_id)

        if str(accession.created_by) != user_id:
            raise ValidationException("Only the creator can update this accession")

        if name is not None:
            if not name.strip():
                raise ValidationException("Accession name cannot be empty")
            accession.name = name.strip()
        if description is not None:
            accession.description = description.strip() if description else None
        if collection_source is not None:
            accession.collection_source = collection_source.strip() if collection_source else None
        if availability_status is not None:
            if availability_status not in ("available", "limited", "unavailable", "reserved"):
                raise ValidationException("Invalid availability status")
            accession.availability_status = availability_status
        if tags is not None:
            accession.tags = tags

        accession.updated_at = datetime.now(UTC)
        return await self.accession_repo.update(accession)


class DeleteAccessionUseCase:
    def __init__(self, accession_repo: AccessionRepositoryInterface):
        self.accession_repo = accession_repo

    async def execute(self, accession_id: str, user_id: str) -> bool:
        accession = await self.accession_repo.get_by_id(accession_id)
        if not accession:
            raise NotFoundException("Accession", accession_id)

        if str(accession.created_by) != user_id:
            raise ValidationException("Only the creator can delete this accession")

        return await self.accession_repo.delete(accession_id)


class SearchAccessionsUseCase:
    def __init__(self, accession_repo: AccessionRepositoryInterface):
        self.accession_repo = accession_repo

    async def execute(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
        filters: dict | None = None,
    ) -> dict:
        if not query or not query.strip():
            raise ValidationException("Search query is required")

        accessions = await self.accession_repo.search(
            query=query, skip=skip, limit=limit, filters=filters
        )

        return {
            "items": [
                {
                    "id": str(a.id),
                    "accession_number": a.accession_number,
                    "name": a.name,
                    "species_id": str(a.species_id),
                    "description": a.description,
                    "availability_status": a.availability_status,
                    "tags": a.tags,
                    "created_at": a.created_at.isoformat(),
                }
                for a in accessions
            ],
            "total": len(accessions),
            "skip": skip,
            "limit": limit,
        }


class CreatePassportDataUseCase:
    def __init__(
        self,
        passport_repo: PassportDataRepositoryInterface,
        accession_repo: AccessionRepositoryInterface,
    ):
        self.passport_repo = passport_repo
        self.accession_repo = accession_repo

    async def execute(
        self,
        accession_id: str,
        institute_code: str | None = None,
        institute_name: str | None = None,
        country_code: str | None = None,
        collection_number: str | None = None,
        collection_source: str | None = None,
        status: str | None = None,
        duplicates: int | None = None,
        remarks: str | None = None,
    ) -> PassportDataModel:
        accession = await self.accession_repo.get_by_id(accession_id)
        if not accession:
            raise NotFoundException("Accession", accession_id)

        existing = await self.passport_repo.get_by_accession_id(accession_id)
        if existing:
            raise ConflictException("Passport data already exists for this accession")

        passport = PassportDataModel(
            accession_id=accession_id,
            institute_code=institute_code.strip() if institute_code else None,
            institute_name=institute_name.strip() if institute_name else None,
            country_code=country_code.strip() if country_code else None,
            collection_number=collection_number.strip() if collection_number else None,
            collection_source=collection_source.strip() if collection_source else None,
            status=status.strip() if status else None,
            duplicates=duplicates,
            remarks=remarks.strip() if remarks else None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.passport_repo.create(passport)


class GetPassportDataUseCase:
    def __init__(self, passport_repo: PassportDataRepositoryInterface):
        self.passport_repo = passport_repo

    async def execute(self, accession_id: str) -> PassportDataModel | None:
        return await self.passport_repo.get_by_accession_id(accession_id)


class UpdatePassportDataUseCase:
    def __init__(self, passport_repo: PassportDataRepositoryInterface):
        self.passport_repo = passport_repo

    async def execute(
        self,
        accession_id: str,
        institute_code: str | None = None,
        institute_name: str | None = None,
        country_code: str | None = None,
        collection_number: str | None = None,
        collection_source: str | None = None,
        status: str | None = None,
        duplicates: int | None = None,
        remarks: str | None = None,
    ) -> PassportDataModel:
        passport = await self.passport_repo.get_by_accession_id(accession_id)
        if not passport:
            raise NotFoundException("Passport data", accession_id)

        if institute_code is not None:
            passport.institute_code = institute_code.strip() if institute_code else None
        if institute_name is not None:
            passport.institute_name = institute_name.strip() if institute_name else None
        if country_code is not None:
            passport.country_code = country_code.strip() if country_code else None
        if collection_number is not None:
            passport.collection_number = collection_number.strip() if collection_number else None
        if collection_source is not None:
            passport.collection_source = collection_source.strip() if collection_source else None
        if status is not None:
            passport.status = status.strip() if status else None
        if duplicates is not None:
            passport.duplicates = duplicates
        if remarks is not None:
            passport.remarks = remarks.strip() if remarks else None

        passport.updated_at = datetime.now(UTC)
        return await self.passport_repo.update(passport)


class CreatePedigreeUseCase:
    def __init__(
        self,
        pedigree_repo: PedigreeRepositoryInterface,
        accession_repo: AccessionRepositoryInterface,
    ):
        self.pedigree_repo = pedigree_repo
        self.accession_repo = accession_repo

    async def execute(
        self,
        accession_id: str,
        parent1_accession_id: str | None = None,
        parent2_accession_id: str | None = None,
        parent1_name: str | None = None,
        parent2_name: str | None = None,
        cross_type: str | None = None,
        generation: int | None = None,
        notes: str | None = None,
    ) -> PedigreeModel:
        accession = await self.accession_repo.get_by_id(accession_id)
        if not accession:
            raise NotFoundException("Accession", accession_id)

        existing = await self.pedigree_repo.get_by_accession_id(accession_id)
        if existing:
            raise ConflictException("Pedigree already exists for this accession")

        if parent1_accession_id:
            parent1 = await self.accession_repo.get_by_id(parent1_accession_id)
            if not parent1:
                raise NotFoundException("Parent1 accession", parent1_accession_id)
            if not parent1_name:
                parent1_name = parent1.name

        if parent2_accession_id:
            parent2 = await self.accession_repo.get_by_id(parent2_accession_id)
            if not parent2:
                raise NotFoundException("Parent2 accession", parent2_accession_id)
            if not parent2_name:
                parent2_name = parent2.name

        pedigree = PedigreeModel(
            accession_id=accession_id,
            parent1_accession_id=parent1_accession_id,
            parent2_accession_id=parent2_accession_id,
            parent1_name=parent1_name,
            parent2_name=parent2_name,
            cross_type=cross_type.strip() if cross_type else None,
            generation=generation,
            notes=notes.strip() if notes else None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.pedigree_repo.create(pedigree)


class GetPedigreeUseCase:
    def __init__(self, pedigree_repo: PedigreeRepositoryInterface):
        self.pedigree_repo = pedigree_repo

    async def execute(self, accession_id: str) -> PedigreeModel | None:
        return await self.pedigree_repo.get_by_accession_id(accession_id)


class GetPedigreeTreeUseCase:
    def __init__(self, pedigree_repo: PedigreeRepositoryInterface):
        self.pedigree_repo = pedigree_repo

    async def execute(self, accession_id: str, depth: int = 3) -> dict:
        ancestors = await self.pedigree_repo.get_ancestors(accession_id, depth)
        descendants = await self.pedigree_repo.get_descendants(accession_id, depth)

        return {
            "accession_id": accession_id,
            "ancestors": [
                {
                    "id": str(p.id),
                    "accession_id": str(p.accession_id),
                    "parent1_accession_id": str(p.parent1_accession_id) if p.parent1_accession_id else None,
                    "parent2_accession_id": str(p.parent2_accession_id) if p.parent2_accession_id else None,
                    "parent1_name": p.parent1_name,
                    "parent2_name": p.parent2_name,
                    "cross_type": p.cross_type,
                    "generation": p.generation,
                }
                for p in ancestors
            ],
            "descendants": [
                {
                    "id": str(p.id),
                    "accession_id": str(p.accession_id),
                    "parent1_accession_id": str(p.parent1_accession_id) if p.parent1_accession_id else None,
                    "parent2_accession_id": str(p.parent2_accession_id) if p.parent2_accession_id else None,
                    "parent1_name": p.parent1_name,
                    "parent2_name": p.parent2_name,
                    "cross_type": p.cross_type,
                    "generation": p.generation,
                }
                for p in descendants
            ],
        }


class CreateSeedStorageUseCase:
    def __init__(
        self,
        storage_repo: SeedStorageRepositoryInterface,
        accession_repo: AccessionRepositoryInterface,
    ):
        self.storage_repo = storage_repo
        self.accession_repo = accession_repo

    async def execute(
        self,
        accession_id: str,
        location: str,
        container_type: str | None = None,
        quantity_grams: float | None = None,
        seed_count: int | None = None,
        storage_conditions: str | None = None,
        storage_date: str | None = None,
        expiry_date: str | None = None,
        viability: float | None = None,
        notes: str | None = None,
    ) -> SeedStorageModel:
        accession = await self.accession_repo.get_by_id(accession_id)
        if not accession:
            raise NotFoundException("Accession", accession_id)

        if not location or not location.strip():
            raise ValidationException("Storage location is required")

        storage = SeedStorageModel(
            accession_id=accession_id,
            location=location.strip(),
            container_type=container_type.strip() if container_type else None,
            quantity_grams=quantity_grams,
            seed_count=seed_count,
            storage_conditions=storage_conditions.strip() if storage_conditions else None,
            storage_date=storage_date,
            expiry_date=expiry_date,
            viability=viability,
            notes=notes.strip() if notes else None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        return await self.storage_repo.create(storage)


class ListSeedStoragesUseCase:
    def __init__(self, storage_repo: SeedStorageRepositoryInterface):
        self.storage_repo = storage_repo

    async def execute(self, accession_id: str) -> list[SeedStorageModel]:
        return await self.storage_repo.list_by_accession(accession_id)


class UpdateSeedStorageUseCase:
    def __init__(self, storage_repo: SeedStorageRepositoryInterface):
        self.storage_repo = storage_repo

    async def execute(
        self,
        storage_id: str,
        location: str | None = None,
        container_type: str | None = None,
        quantity_grams: float | None = None,
        seed_count: int | None = None,
        storage_conditions: str | None = None,
        expiry_date: str | None = None,
        viability: float | None = None,
        notes: str | None = None,
    ) -> SeedStorageModel:
        storage = await self.storage_repo.get_by_id(storage_id)
        if not storage:
            raise NotFoundException("Seed storage", storage_id)

        if location is not None:
            if not location.strip():
                raise ValidationException("Storage location cannot be empty")
            storage.location = location.strip()
        if container_type is not None:
            storage.container_type = container_type.strip() if container_type else None
        if quantity_grams is not None:
            storage.quantity_grams = quantity_grams
        if seed_count is not None:
            storage.seed_count = seed_count
        if storage_conditions is not None:
            storage.storage_conditions = storage_conditions.strip() if storage_conditions else None
        if expiry_date is not None:
            storage.expiry_date = expiry_date
        if viability is not None:
            storage.viability = viability
        if notes is not None:
            storage.notes = notes.strip() if notes else None

        storage.updated_at = datetime.now(UTC)
        return await self.storage_repo.update(storage)


class DeleteSeedStorageUseCase:
    def __init__(self, storage_repo: SeedStorageRepositoryInterface):
        self.storage_repo = storage_repo

    async def execute(self, storage_id: str) -> bool:
        storage = await self.storage_repo.get_by_id(storage_id)
        if not storage:
            raise NotFoundException("Seed storage", storage_id)

        return await self.storage_repo.delete(storage_id)


class UploadGermplasmImageUseCase:
    def __init__(
        self,
        image_repo: GermplasmImageRepositoryInterface,
        accession_repo: AccessionRepositoryInterface,
    ):
        self.image_repo = image_repo
        self.accession_repo = accession_repo

    async def execute(
        self,
        accession_id: str,
        filename: str,
        original_filename: str,
        mime_type: str,
        file_size: int,
        storage_path: str,
        thumbnail_path: str | None = None,
        caption: str | None = None,
        image_type: str | None = None,
        taken_at: datetime | None = None,
        metadata: dict | None = None,
        uploaded_by: str | None = None,
    ) -> GermplasmImageModel:
        accession = await self.accession_repo.get_by_id(accession_id)
        if not accession:
            raise NotFoundException("Accession", accession_id)

        image = GermplasmImageModel(
            accession_id=accession_id,
            filename=filename,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path,
            thumbnail_path=thumbnail_path,
            caption=caption.strip() if caption else None,
            image_type=image_type.strip() if image_type else None,
            taken_at=taken_at,
            metadata_json=metadata,
            uploaded_by=uploaded_by,
            created_at=datetime.now(UTC),
        )

        return await self.image_repo.create(image)


class ListGermplasmImagesUseCase:
    def __init__(self, image_repo: GermplasmImageRepositoryInterface):
        self.image_repo = image_repo

    async def execute(self, accession_id: str) -> list[GermplasmImageModel]:
        return await self.image_repo.list_by_accession(accession_id)


class DeleteGermplasmImageUseCase:
    def __init__(self, image_repo: GermplasmImageRepositoryInterface):
        self.image_repo = image_repo

    async def execute(self, image_id: str, user_id: str) -> bool:
        image = await self.image_repo.get_by_id(image_id)
        if not image:
            raise NotFoundException("Image", image_id)

        if str(image.uploaded_by) != user_id:
            raise ValidationException("Only the creator can delete this image")

        return await self.image_repo.delete(image_id)


class UploadGermplasmFileUseCase:
    def __init__(
        self,
        file_repo: GermplasmFileRepositoryInterface,
        accession_repo: AccessionRepositoryInterface,
    ):
        self.file_repo = file_repo
        self.accession_repo = accession_repo

    async def execute(
        self,
        accession_id: str,
        filename: str,
        original_filename: str,
        mime_type: str,
        file_size: int,
        storage_path: str,
        description: str | None = None,
        file_type: str | None = None,
        uploaded_by: str | None = None,
    ) -> GermplasmFileModel:
        accession = await self.accession_repo.get_by_id(accession_id)
        if not accession:
            raise NotFoundException("Accession", accession_id)

        file = GermplasmFileModel(
            accession_id=accession_id,
            filename=filename,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path,
            description=description.strip() if description else None,
            file_type=file_type.strip() if file_type else None,
            uploaded_by=uploaded_by,
            created_at=datetime.now(UTC),
        )

        return await self.file_repo.create(file)


class ListGermplasmFilesUseCase:
    def __init__(self, file_repo: GermplasmFileRepositoryInterface):
        self.file_repo = file_repo

    async def execute(self, accession_id: str) -> list[GermplasmFileModel]:
        return await self.file_repo.list_by_accession(accession_id)


class DeleteGermplasmFileUseCase:
    def __init__(self, file_repo: GermplasmFileRepositoryInterface):
        self.file_repo = file_repo

    async def execute(self, file_id: str, user_id: str) -> bool:
        file = await self.file_repo.get_by_id(file_id)
        if not file:
            raise NotFoundException("File", file_id)

        if str(file.uploaded_by) != user_id:
            raise ValidationException("Only the creator can delete this file")

        return await self.file_repo.delete(file_id)
