from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.organization_repository import OrganizationRepository
from app.domain.models.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    Organization,
)


class OrganizationService:
    def __init__(self):
        self.repository = OrganizationRepository()

    async def get(
        self, db: AsyncSession, organization_id: int
    ) -> Optional[Organization]:
        return await self.repository.get_with_details(db, organization_id)

    async def get_with_details(
        self, db: AsyncSession, organization_id: int
    ) -> Optional[Organization]:
        return await self.repository.get_with_details(db, organization_id)

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        return await self.repository.get_multi_with_relations(
            db, skip=skip, limit=limit
        )

    async def create(
        self, db: AsyncSession, organization_in: OrganizationCreate
    ) -> Organization:
        return await self.repository.create_with_relations(db, obj_in=organization_in)

    async def update(
        self,
        db: AsyncSession,
        organization_id: int,
        organization_in: OrganizationUpdate,
    ) -> Optional[Organization]:
        db_organization = await self.repository.get(db, organization_id)
        if not db_organization:
            return None
        return await self.repository.update_with_relations(
            db, db_obj=db_organization, obj_in=organization_in
        )

    async def delete(self, db: AsyncSession, organization_id: int) -> bool:
        db_organization = await self.repository.remove(db, id=organization_id)
        return db_organization is not None

    async def get_by_building(
        self, db: AsyncSession, building_id: int
    ) -> List[Organization]:
        return await self.repository.get_by_building(db, building_id)

    async def get_by_activity(
        self, db: AsyncSession, activity_id: int, include_children: bool = False
    ) -> List[Organization]:
        return await self.repository.get_by_activity(db, activity_id, include_children)

    async def search_by_name(self, db: AsyncSession, name: str) -> List[Organization]:
        return await self.repository.search_by_name(db, name)

    async def get_by_location(
        self,
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius: float = None,
        min_lat: float = None,
        min_lon: float = None,
        max_lat: float = None,
        max_lon: float = None,
    ) -> List[Organization]:
        return await self.repository.get_by_location(
            db,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            min_lat=min_lat,
            min_lon=min_lon,
            max_lat=max_lat,
            max_lon=max_lon,
        )

    async def get_by_activity_name(
        self, db: AsyncSession, activity_name: str, include_children: bool = True
    ) -> List[Organization]:
        return await self.repository.get_by_activity_name(
            db, activity_name=activity_name, include_children=include_children
        )
