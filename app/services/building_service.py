from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.building_repository import BuildingRepository
from app.domain.models.building import BuildingCreate, BuildingUpdate, Building


class BuildingService:
    def __init__(self):
        self.repository = BuildingRepository()
    
    async def get(self, db: AsyncSession, building_id: int) -> Optional[Building]:
        return await self.repository.get(db, building_id)
    
    async def get_with_organizations(self, db: AsyncSession, building_id: int) -> Optional[Building]:
        return await self.repository.get_with_organizations(db, building_id)
    
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Building]:
        return await self.repository.get_multi(db, skip=skip, limit=limit)
    
    async def create(self, db: AsyncSession, building_in: BuildingCreate) -> Building:
        return await self.repository.create(db, obj_in=building_in)
    
    async def update(self, db: AsyncSession, building_id: int, building_in: BuildingUpdate) -> Optional[Building]:
        db_building = await self.repository.get(db, building_id)
        if not db_building:
            return None
        return await self.repository.update(db, db_obj=db_building, obj_in=building_in)
    
    async def delete(self, db: AsyncSession, building_id: int) -> bool:
        db_building = await self.repository.remove(db, id=building_id)
        return db_building is not None
    
    async def get_buildings_in_radius(
        self, db: AsyncSession, latitude: float, longitude: float, radius: float
    ) -> List[Building]:
        return await self.repository.get_buildings_in_radius(db, latitude, longitude, radius)
    
    async def get_buildings_in_rectangle(
        self, db: AsyncSession, min_lat: float, min_lon: float, max_lat: float, max_lon: float
    ) -> List[Building]:
        return await self.repository.get_buildings_in_rectangle(db, min_lat, min_lon, max_lat, max_lon)
