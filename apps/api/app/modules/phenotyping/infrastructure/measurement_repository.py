from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.phenotyping.domain.interfaces import MeasurementRepositoryInterface
from app.modules.phenotyping.domain.models import MeasurementModel, TraitModel


class MeasurementRepository(MeasurementRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, measurement: MeasurementModel) -> MeasurementModel:
        self.db.add(measurement)
        await self.db.flush()
        await self.db.refresh(measurement)
        return measurement

    async def bulk_create(self, measurements: list[MeasurementModel]) -> list[MeasurementModel]:
        self.db.add_all(measurements)
        await self.db.flush()
        for m in measurements:
            await self.db.refresh(m)
        return measurements

    async def get_by_id(self, measurement_id: str) -> MeasurementModel | None:
        result = await self.db.execute(
            select(MeasurementModel).where(MeasurementModel.id == measurement_id)
        )
        return result.scalar_one_or_none()

    async def list_by_experiment(
        self,
        experiment_id: str,
        skip: int = 0,
        limit: int = 100,
        trait_id: str | None = None,
        accession_id: str | None = None,
    ) -> list[MeasurementModel]:
        query = select(MeasurementModel).where(
            MeasurementModel.experiment_id == experiment_id
        )

        if trait_id:
            query = query.where(MeasurementModel.trait_id == trait_id)
        if accession_id:
            query = query.where(MeasurementModel.accession_id == accession_id)

        query = query.order_by(MeasurementModel.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_experiment(
        self,
        experiment_id: str,
        trait_id: str | None = None,
        accession_id: str | None = None,
    ) -> int:
        query = select(func.count(MeasurementModel.id)).where(
            MeasurementModel.experiment_id == experiment_id
        )

        if trait_id:
            query = query.where(MeasurementModel.trait_id == trait_id)
        if accession_id:
            query = query.where(MeasurementModel.accession_id == accession_id)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, measurement: MeasurementModel) -> MeasurementModel:
        await self.db.flush()
        await self.db.refresh(measurement)
        return measurement

    async def delete(self, measurement_id: str) -> bool:
        measurement = await self.get_by_id(measurement_id)
        if not measurement:
            return False
        await self.db.delete(measurement)
        return True

    async def get_experiment_summary(self, experiment_id: str) -> dict:
        total_q = select(func.count(MeasurementModel.id)).where(
            MeasurementModel.experiment_id == experiment_id
        )
        total_result = await self.db.execute(total_q)
        total_measurements = total_result.scalar_one()

        trait_q = select(func.count(func.distinct(MeasurementModel.trait_id))).where(
            MeasurementModel.experiment_id == experiment_id
        )
        trait_result = await self.db.execute(trait_q)
        trait_count = trait_result.scalar_one()

        acc_q = select(func.count(func.distinct(MeasurementModel.accession_id))).where(
            MeasurementModel.experiment_id == experiment_id,
            MeasurementModel.accession_id.isnot(None),
        )
        acc_result = await self.db.execute(acc_q)
        accession_count = acc_result.scalar_one()

        traits_summary = []
        traits_result = await self.db.execute(
            select(TraitModel).where(TraitModel.experiment_id == experiment_id)
        )
        traits = traits_result.scalars().all()
        for trait in traits:
            min_q = select(func.min(MeasurementModel.value_numeric)).where(
                MeasurementModel.trait_id == trait.id,
                MeasurementModel.value_numeric.isnot(None),
            )
            max_q = select(func.max(MeasurementModel.value_numeric)).where(
                MeasurementModel.trait_id == trait.id,
                MeasurementModel.value_numeric.isnot(None),
            )
            avg_q = select(func.avg(MeasurementModel.value_numeric)).where(
                MeasurementModel.trait_id == trait.id,
                MeasurementModel.value_numeric.isnot(None),
            )
            count_q = select(func.count(MeasurementModel.id)).where(
                MeasurementModel.trait_id == trait.id
            )

            min_val = (await self.db.execute(min_q)).scalar_one()
            max_val = (await self.db.execute(max_q)).scalar_one()
            avg_val = (await self.db.execute(avg_q)).scalar_one()
            count_val = (await self.db.execute(count_q)).scalar_one()

            traits_summary.append({
                "trait_id": str(trait.id),
                "trait_name": trait.name,
                "unit": trait.unit,
                "count": count_val,
                "min": float(min_val) if min_val is not None else None,
                "max": float(max_val) if max_val is not None else None,
                "mean": round(float(avg_val), 2) if avg_val is not None else None,
            })

        return {
            "experiment_id": experiment_id,
            "total_measurements": total_measurements,
            "trait_count": trait_count,
            "accession_count": accession_count,
            "traits_summary": traits_summary,
        }
