from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.germplasm.domain.interfaces import SpeciesRepositoryInterface
from app.modules.germplasm.domain.models import SpeciesModel


class SpeciesRepository(SpeciesRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, species: SpeciesModel) -> SpeciesModel:
        self.db.add(species)
        await self.db.commit()
        await self.db.refresh(species)
        return species

    async def get_by_id(self, species_id: str) -> SpeciesModel | None:
        result = await self.db.execute(
            select(SpeciesModel).where(SpeciesModel.id == species_id)
        )
        return result.scalar_one_or_none()

    async def get_by_scientific_name(self, scientific_name: str) -> SpeciesModel | None:
        result = await self.db.execute(
            select(SpeciesModel).where(
                func.lower(SpeciesModel.scientific_name) == func.lower(scientific_name)
            )
        )
        return result.scalar_one_or_none()

    async def list_species(
        self, skip: int = 0, limit: int = 20, search: str | None = None
    ) -> list[SpeciesModel]:
        query = select(SpeciesModel)
        if search:
            query = query.where(
                SpeciesModel.common_name.ilike(f"%{search}%")
                | SpeciesModel.scientific_name.ilike(f"%{search}%")
                | SpeciesModel.family.ilike(f"%{search}%")
            )
        query = query.order_by(SpeciesModel.common_name).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_species(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(SpeciesModel)
        if search:
            query = query.where(
                SpeciesModel.common_name.ilike(f"%{search}%")
                | SpeciesModel.scientific_name.ilike(f"%{search}%")
                | SpeciesModel.family.ilike(f"%{search}%")
            )
        result = await self.db.execute(query)
        return result.scalar()

    async def update(self, species: SpeciesModel) -> SpeciesModel:
        await self.db.commit()
        await self.db.refresh(species)
        return species

    async def delete(self, species_id: str) -> bool:
        species = await self.get_by_id(species_id)
        if not species:
            return False
        await self.db.delete(species)
        await self.db.commit()
        return True
