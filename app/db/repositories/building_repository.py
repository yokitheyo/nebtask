from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.repositories.base_repository import BaseRepository
from app.db.models import Building
from app.domain.models.building import BuildingCreate, BuildingUpdate


class BuildingRepository(BaseRepository[Building, BuildingCreate, BuildingUpdate]):
    def __init__(self):
        super().__init__(Building)
    
    async def get_with_organizations(self, db: AsyncSession, building_id: int) -> Optional[Building]:
        query = (
            select(Building)
            .options(selectinload(Building.organizations))
            .where(Building.id == building_id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_buildings_in_radius(
        self, db: AsyncSession, latitude: float, longitude: float, radius: float
    ) -> List[Building]:
        radius_degrees = radius / 111320
        
        min_lat = latitude - radius_degrees
        max_lat = latitude + radius_degrees
        min_lon = longitude - radius_degrees
        max_lon = longitude + radius_degrees
        
        query = (
            select(Building)
            .where(
                and_(
                    Building.latitude >= min_lat,
                    Building.latitude <= max_lat,
                    Building.longitude >= min_lon,
                    Building.longitude <= max_lon
                )
            )
        )
        result = await db.execute(query)
        buildings = result.scalars().all()
        
        result_buildings = []
        for building in buildings:
            distance = ((building.latitude - latitude) ** 2 + 
                       (building.longitude - longitude) ** 2) ** 0.5
            if distance <= radius_degrees:
                result_buildings.append(building)
        
        return result_buildings
    
    async def get_buildings_in_rectangle(
        self, db: AsyncSession, min_lat: float, min_lon: float, max_lat: float, max_lon: float
    ) -> List[Building]:
        query = (
            select(Building)
            .where(
                and_(
                    Building.latitude >= min_lat,
                    Building.latitude <= max_lat,
                    Building.longitude >= min_lon,
                    Building.longitude <= max_lon
                )
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
