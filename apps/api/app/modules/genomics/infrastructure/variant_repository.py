from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.genomics.domain.interfaces import VariantRepositoryInterface
from app.modules.genomics.domain.models import VariantModel


class VariantRepository(VariantRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, variant: VariantModel) -> VariantModel:
        self.db.add(variant)
        await self.db.flush()
        await self.db.refresh(variant)
        return variant

    async def bulk_create(self, variants: list[VariantModel]) -> list[VariantModel]:
        self.db.add_all(variants)
        await self.db.flush()
        for v in variants:
            await self.db.refresh(v)
        return variants

    async def get_by_id(self, variant_id: str) -> VariantModel | None:
        result = await self.db.execute(
            select(VariantModel).where(VariantModel.id == variant_id)
        )
        return result.scalar_one_or_none()

    async def list_by_sequence(
        self,
        sequence_id: str,
        skip: int = 0,
        limit: int = 100,
        chromosome: str | None = None,
        variant_type: str | None = None,
        gene_name: str | None = None,
    ) -> list[VariantModel]:
        query = select(VariantModel).where(VariantModel.sequence_id == sequence_id)

        if chromosome:
            query = query.where(VariantModel.chromosome == chromosome)
        if variant_type:
            query = query.where(VariantModel.variant_type == variant_type)
        if gene_name:
            query = query.where(VariantModel.gene_name.ilike(f"%{gene_name}%"))

        query = query.order_by(VariantModel.chromosome, VariantModel.position)
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_sequence(
        self,
        sequence_id: str,
        chromosome: str | None = None,
        variant_type: str | None = None,
        gene_name: str | None = None,
    ) -> int:
        query = select(func.count(VariantModel.id)).where(
            VariantModel.sequence_id == sequence_id
        )

        if chromosome:
            query = query.where(VariantModel.chromosome == chromosome)
        if variant_type:
            query = query.where(VariantModel.variant_type == variant_type)
        if gene_name:
            query = query.where(VariantModel.gene_name.ilike(f"%{gene_name}%"))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def search(
        self,
        sequence_id: str,
        chromosome: str | None = None,
        start: int | None = None,
        end: int | None = None,
        variant_type: str | None = None,
        gene_name: str | None = None,
        min_quality: float | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[VariantModel]:
        query = select(VariantModel).where(VariantModel.sequence_id == sequence_id)

        if chromosome:
            query = query.where(VariantModel.chromosome == chromosome)
        if start is not None:
            query = query.where(VariantModel.position >= start)
        if end is not None:
            query = query.where(VariantModel.position <= end)
        if variant_type:
            query = query.where(VariantModel.variant_type == variant_type)
        if gene_name:
            query = query.where(VariantModel.gene_name.ilike(f"%{gene_name}%"))
        if min_quality is not None:
            query = query.where(VariantModel.quality >= min_quality)

        query = query.order_by(VariantModel.chromosome, VariantModel.position)
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, variant: VariantModel) -> VariantModel:
        await self.db.flush()
        await self.db.refresh(variant)
        return variant

    async def delete(self, variant_id: str) -> bool:
        variant = await self.get_by_id(variant_id)
        if not variant:
            return False
        await self.db.delete(variant)
        return True
