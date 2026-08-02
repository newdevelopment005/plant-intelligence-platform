from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.genomics.domain.interfaces import GeneAnnotationRepositoryInterface
from app.modules.genomics.domain.models import GeneAnnotationModel


class GeneAnnotationRepository(GeneAnnotationRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, annotation: GeneAnnotationModel) -> GeneAnnotationModel:
        self.db.add(annotation)
        await self.db.flush()
        await self.db.refresh(annotation)
        return annotation

    async def get_by_id(self, annotation_id: str) -> GeneAnnotationModel | None:
        result = await self.db.execute(
            select(GeneAnnotationModel).where(GeneAnnotationModel.id == annotation_id)
        )
        return result.scalar_one_or_none()

    async def list_by_sequence(
        self,
        sequence_id: str,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> list[GeneAnnotationModel]:
        query = select(GeneAnnotationModel).where(
            GeneAnnotationModel.sequence_id == sequence_id
        )

        if search:
            query = query.where(
                GeneAnnotationModel.gene_symbol.ilike(f"%{search}%")
                | GeneAnnotationModel.gene_name.ilike(f"%{search}%")
            )

        query = query.order_by(GeneAnnotationModel.gene_symbol)
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_sequence(
        self,
        sequence_id: str,
        search: str | None = None,
    ) -> int:
        query = select(func.count(GeneAnnotationModel.id)).where(
            GeneAnnotationModel.sequence_id == sequence_id
        )

        if search:
            query = query.where(
                GeneAnnotationModel.gene_symbol.ilike(f"%{search}%")
                | GeneAnnotationModel.gene_name.ilike(f"%{search}%")
            )

        result = await self.db.execute(query)
        return result.scalar_one()

    async def search_by_gene(
        self,
        sequence_id: str,
        gene_symbol: str,
    ) -> GeneAnnotationModel | None:
        result = await self.db.execute(
            select(GeneAnnotationModel).where(
                GeneAnnotationModel.sequence_id == sequence_id,
                GeneAnnotationModel.gene_symbol == gene_symbol,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, annotation: GeneAnnotationModel) -> GeneAnnotationModel:
        await self.db.flush()
        await self.db.refresh(annotation)
        return annotation

    async def delete(self, annotation_id: str) -> bool:
        annotation = await self.get_by_id(annotation_id)
        if not annotation:
            return False
        await self.db.delete(annotation)
        return True
