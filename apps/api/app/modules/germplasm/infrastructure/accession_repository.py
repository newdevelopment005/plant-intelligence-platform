from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.germplasm.domain.interfaces import AccessionRepositoryInterface
from app.modules.germplasm.domain.models import AccessionModel


class AccessionRepository(AccessionRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, accession: AccessionModel) -> AccessionModel:
        self.db.add(accession)
        await self.db.commit()
        await self.db.refresh(accession)
        return accession

    async def get_by_id(self, accession_id: str) -> AccessionModel | None:
        result = await self.db.execute(
            select(AccessionModel)
            .options(
                selectinload(AccessionModel.species),
                selectinload(AccessionModel.passport_data),
                selectinload(AccessionModel.pedigree),
                selectinload(AccessionModel.seed_storages),
            )
            .where(AccessionModel.id == accession_id)
        )
        return result.scalar_one_or_none()

    async def get_by_accession_number(self, accession_number: str) -> AccessionModel | None:
        result = await self.db.execute(
            select(AccessionModel).where(
                func.lower(AccessionModel.accession_number) == func.lower(accession_number)
            )
        )
        return result.scalar_one_or_none()

    async def list_accessions(
        self,
        skip: int = 0,
        limit: int = 20,
        species_id: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[AccessionModel]:
        query = select(AccessionModel)
        if species_id:
            query = query.where(AccessionModel.species_id == species_id)
        if project_id:
            query = query.where(AccessionModel.project_id == project_id)
        if status:
            query = query.where(AccessionModel.availability_status == status)
        if user_id:
            query = query.where(AccessionModel.created_by == user_id)
        if search:
            query = query.where(
                AccessionModel.name.ilike(f"%{search}%")
                | AccessionModel.accession_number.ilike(f"%{search}%")
                | AccessionModel.description.ilike(f"%{search}%")
            )
        query = query.order_by(AccessionModel.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_accessions(
        self,
        species_id: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count()).select_from(AccessionModel)
        if species_id:
            query = query.where(AccessionModel.species_id == species_id)
        if project_id:
            query = query.where(AccessionModel.project_id == project_id)
        if status:
            query = query.where(AccessionModel.availability_status == status)
        if user_id:
            query = query.where(AccessionModel.created_by == user_id)
        if search:
            query = query.where(
                AccessionModel.name.ilike(f"%{search}%")
                | AccessionModel.accession_number.ilike(f"%{search}%")
                | AccessionModel.description.ilike(f"%{search}%")
            )
        result = await self.db.execute(query)
        return result.scalar()

    async def update(self, accession: AccessionModel) -> AccessionModel:
        await self.db.commit()
        await self.db.refresh(accession)
        return accession

    async def delete(self, accession_id: str) -> bool:
        accession = await self.get_by_id(accession_id)
        if not accession:
            return False
        await self.db.delete(accession)
        await self.db.commit()
        return True

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
        filters: dict | None = None,
    ) -> list[AccessionModel]:
        stmt = select(AccessionModel)
        search_filter = (
            AccessionModel.name.ilike(f"%{query}%")
            | AccessionModel.accession_number.ilike(f"%{query}%")
            | AccessionModel.description.ilike(f"%{query}%")
        )
        stmt = stmt.where(search_filter)

        if filters:
            if "species_id" in filters:
                stmt = stmt.where(AccessionModel.species_id == filters["species_id"])
            if "status" in filters:
                stmt = stmt.where(AccessionModel.availability_status == filters["status"])
            if "project_id" in filters:
                stmt = stmt.where(AccessionModel.project_id == filters["project_id"])

        stmt = stmt.order_by(AccessionModel.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
