from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.germplasm.domain.interfaces import (
    GermplasmFileRepositoryInterface,
    GermplasmImageRepositoryInterface,
    PassportDataRepositoryInterface,
    PedigreeRepositoryInterface,
    SeedStorageRepositoryInterface,
)
from app.modules.germplasm.domain.models import (
    GermplasmFileModel,
    GermplasmImageModel,
    PassportDataModel,
    PedigreeModel,
    SeedStorageModel,
)


class PassportDataRepository(PassportDataRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, passport: PassportDataModel) -> PassportDataModel:
        self.db.add(passport)
        await self.db.commit()
        await self.db.refresh(passport)
        return passport

    async def get_by_accession_id(self, accession_id: str) -> PassportDataModel | None:
        result = await self.db.execute(
            select(PassportDataModel).where(PassportDataModel.accession_id == accession_id)
        )
        return result.scalar_one_or_none()

    async def update(self, passport: PassportDataModel) -> PassportDataModel:
        await self.db.commit()
        await self.db.refresh(passport)
        return passport

    async def delete(self, accession_id: str) -> bool:
        passport = await self.get_by_accession_id(accession_id)
        if not passport:
            return False
        await self.db.delete(passport)
        await self.db.commit()
        return True


class PedigreeRepository(PedigreeRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, pedigree: PedigreeModel) -> PedigreeModel:
        self.db.add(pedigree)
        await self.db.commit()
        await self.db.refresh(pedigree)
        return pedigree

    async def get_by_accession_id(self, accession_id: str) -> PedigreeModel | None:
        result = await self.db.execute(
            select(PedigreeModel).where(PedigreeModel.accession_id == accession_id)
        )
        return result.scalar_one_or_none()

    async def get_ancestors(self, accession_id: str, depth: int = 3) -> list[PedigreeModel]:
        ancestors = []
        current_id = accession_id
        for _ in range(depth):
            pedigree = await self.get_by_accession_id(current_id)
            if not pedigree:
                break
            ancestors.append(pedigree)
            if pedigree.parent1_accession_id:
                current_id = str(pedigree.parent1_accession_id)
            else:
                break
        return ancestors

    async def get_descendants(self, accession_id: str, depth: int = 3) -> list[PedigreeModel]:
        descendants = []
        queue = [accession_id]
        for _ in range(depth):
            next_queue = []
            for current_id in queue:
                result = await self.db.execute(
                    select(PedigreeModel).where(
                        (PedigreeModel.parent1_accession_id == current_id)
                        | (PedigreeModel.parent2_accession_id == current_id)
                    )
                )
                found = list(result.scalars().all())
                descendants.extend(found)
                next_queue.extend([str(p.accession_id) for p in found])
            queue = next_queue
            if not queue:
                break
        return descendants

    async def update(self, pedigree: PedigreeModel) -> PedigreeModel:
        await self.db.commit()
        await self.db.refresh(pedigree)
        return pedigree

    async def delete(self, accession_id: str) -> bool:
        pedigree = await self.get_by_accession_id(accession_id)
        if not pedigree:
            return False
        await self.db.delete(pedigree)
        await self.db.commit()
        return True


class SeedStorageRepository(SeedStorageRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, storage: SeedStorageModel) -> SeedStorageModel:
        self.db.add(storage)
        await self.db.commit()
        await self.db.refresh(storage)
        return storage

    async def get_by_id(self, storage_id: str) -> SeedStorageModel | None:
        result = await self.db.execute(
            select(SeedStorageModel).where(SeedStorageModel.id == storage_id)
        )
        return result.scalar_one_or_none()

    async def list_by_accession(self, accession_id: str) -> list[SeedStorageModel]:
        result = await self.db.execute(
            select(SeedStorageModel)
            .where(SeedStorageModel.accession_id == accession_id)
            .order_by(SeedStorageModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, storage: SeedStorageModel) -> SeedStorageModel:
        await self.db.commit()
        await self.db.refresh(storage)
        return storage

    async def delete(self, storage_id: str) -> bool:
        storage = await self.get_by_id(storage_id)
        if not storage:
            return False
        await self.db.delete(storage)
        await self.db.commit()
        return True


class GermplasmImageRepository(GermplasmImageRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, image: GermplasmImageModel) -> GermplasmImageModel:
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def get_by_id(self, image_id: str) -> GermplasmImageModel | None:
        result = await self.db.execute(
            select(GermplasmImageModel).where(GermplasmImageModel.id == image_id)
        )
        return result.scalar_one_or_none()

    async def list_by_accession(self, accession_id: str) -> list[GermplasmImageModel]:
        result = await self.db.execute(
            select(GermplasmImageModel)
            .where(GermplasmImageModel.accession_id == accession_id)
            .order_by(GermplasmImageModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, image_id: str) -> bool:
        image = await self.get_by_id(image_id)
        if not image:
            return False
        await self.db.delete(image)
        await self.db.commit()
        return True


class GermplasmFileRepository(GermplasmFileRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, file: GermplasmFileModel) -> GermplasmFileModel:
        self.db.add(file)
        await self.db.commit()
        await self.db.refresh(file)
        return file

    async def get_by_id(self, file_id: str) -> GermplasmFileModel | None:
        result = await self.db.execute(
            select(GermplasmFileModel).where(GermplasmFileModel.id == file_id)
        )
        return result.scalar_one_or_none()

    async def list_by_accession(self, accession_id: str) -> list[GermplasmFileModel]:
        result = await self.db.execute(
            select(GermplasmFileModel)
            .where(GermplasmFileModel.accession_id == accession_id)
            .order_by(GermplasmFileModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, file_id: str) -> bool:
        file = await self.get_by_id(file_id)
        if not file:
            return False
        await self.db.delete(file)
        await self.db.commit()
        return True
