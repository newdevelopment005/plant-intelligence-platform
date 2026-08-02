from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.image_analysis.domain.interfaces import PlantImageRepositoryInterface
from app.modules.image_analysis.domain.models import PlantImageModel


class PlantImageRepository(PlantImageRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, image: PlantImageModel) -> PlantImageModel:
        self.db.add(image)
        await self.db.flush()
        await self.db.refresh(image)
        return image

    async def get_by_id(self, image_id: str) -> PlantImageModel | None:
        result = await self.db.execute(
            select(PlantImageModel).where(PlantImageModel.id == image_id)
        )
        return result.scalar_one_or_none()

    async def list_images(
        self,
        skip: int = 0,
        limit: int = 20,
        image_type: str | None = None,
        species: str | None = None,
        project_id: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> list[PlantImageModel]:
        query = select(PlantImageModel)
        if image_type:
            query = query.where(PlantImageModel.image_type == image_type)
        if species:
            query = query.where(PlantImageModel.species.ilike(f"%{species}%"))
        if project_id:
            query = query.where(PlantImageModel.project_id == project_id)
        if source_module:
            query = query.where(PlantImageModel.source_module == source_module)
        if search:
            query = query.where(PlantImageModel.name.ilike(f"%{search}%"))
        if user_id:
            query = query.where(PlantImageModel.created_by == user_id)
        query = query.order_by(PlantImageModel.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_images(
        self,
        image_type: str | None = None,
        species: str | None = None,
        project_id: str | None = None,
        source_module: str | None = None,
        search: str | None = None,
        user_id: str | None = None,
    ) -> int:
        query = select(func.count()).select_from(PlantImageModel)
        if image_type:
            query = query.where(PlantImageModel.image_type == image_type)
        if species:
            query = query.where(PlantImageModel.species.ilike(f"%{species}%"))
        if project_id:
            query = query.where(PlantImageModel.project_id == project_id)
        if source_module:
            query = query.where(PlantImageModel.source_module == source_module)
        if search:
            query = query.where(PlantImageModel.name.ilike(f"%{search}%"))
        if user_id:
            query = query.where(PlantImageModel.created_by == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update(self, image: PlantImageModel) -> PlantImageModel:
        await self.db.flush()
        await self.db.refresh(image)
        return image

    async def delete(self, image_id: str) -> bool:
        image = await self.get_by_id(image_id)
        if not image:
            return False
        await self.db.delete(image)
        return True
