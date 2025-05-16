from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.repositories.base_repository import BaseRepository
from app.db.models import Organization, PhoneNumber, Activity, Building, organization_activity
from app.domain.models.organization import OrganizationCreate, OrganizationUpdate


class OrganizationRepository(
    BaseRepository[Organization, OrganizationCreate, OrganizationUpdate]
):

    def __init__(self):
        super().__init__(Organization)

    async def get_multi_with_relations(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        query = (
            select(Organization)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_details(
        self, db: AsyncSession, organization_id: int
    ) -> Optional[Organization]:
        query = (
            select(Organization)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
            )
            .where(Organization.id == organization_id)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def create_with_relations(
        self, db: AsyncSession, *, obj_in: OrganizationCreate
    ) -> Organization:
        obj_in_data = obj_in.model_dump(exclude={"phone_numbers", "activity_ids"})
        db_obj = Organization(**obj_in_data)
        db.add(db_obj)
        await db.flush()

        for phone in obj_in.phone_numbers:
            db_phone = PhoneNumber(number=phone.number, organization_id=db_obj.id)
            db.add(db_phone)

        if obj_in.activity_ids:
            query = select(Activity).where(Activity.id.in_(obj_in.activity_ids))
            result = await db.execute(query)
            activities = result.scalars().all()
            
            await db.refresh(db_obj, attribute_names=["activities"])
            
            db_obj.activities.extend(activities)
            await db.flush()

        await db.commit()
        
        await db.refresh(db_obj, attribute_names=["phone_numbers", "activities", "building"])
        
        return db_obj

    async def update_with_relations(
        self, db: AsyncSession, *, db_obj: Organization, obj_in: OrganizationUpdate
    ) -> Organization:
        update_data = obj_in.model_dump(exclude_unset=True)

        if "phone_numbers" in update_data:
            phone_numbers = update_data.pop("phone_numbers")

            await db.execute(delete(PhoneNumber).where(PhoneNumber.organization_id == db_obj.id))

            for phone in phone_numbers:
                db.add(PhoneNumber(number=phone["number"], organization_id=db_obj.id))

        if "activity_ids" in update_data:
            activity_ids = update_data.pop("activity_ids")
            
            stmt = select(Activity).where(Activity.id.in_(activity_ids)).options(selectinload(Activity.children))
            result = await db.execute(stmt)
            activities = result.scalars().all()
            
            await db.execute(delete(organization_activity).where(organization_activity.c.organization_id == db_obj.id))
            
            await db.refresh(db_obj, attribute_names=["activities"])
            
            db_obj.activities.extend(activities)
            await db.flush()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        
        await db.refresh(db_obj, attribute_names=["phone_numbers", "activities", "building"])
        
        return db_obj

    async def get_by_building(
        self, db: AsyncSession, building_id: int
    ) -> List[Organization]:
        query = (
            select(Organization)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
            )
            .where(Organization.building_id == building_id)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_activity(
        self, db: AsyncSession, activity_id: int, include_children: bool = False
    ) -> List[Organization]:
        if not include_children:
            query = (
                select(Organization)
                .options(
                    selectinload(Organization.building),
                    selectinload(Organization.phone_numbers),
                    selectinload(Organization.activities),
                )
                .where(Organization.activities.any(Activity.id == activity_id))
            )
            result = await db.execute(query)
            return result.scalars().all()

        from app.db.repositories.activity_repository import ActivityRepository

        activity_repo = ActivityRepository()
        activity_ids = await activity_repo.get_all_child_ids(db, activity_id)

        query = (
            select(Organization)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
            )
            .where(Organization.activities.any(Activity.id.in_(activity_ids)))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def search_by_name(self, db: AsyncSession, name: str) -> List[Organization]:
        query = (
            select(Organization)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
            )
            .where(func.lower(Organization.name).contains(func.lower(name)))
        )
        result = await db.execute(query)
        return result.scalars().all()

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
        from app.db.repositories.building_repository import BuildingRepository

        building_repo = BuildingRepository()

        if radius is not None:
            buildings = await building_repo.get_buildings_in_radius(
                db, latitude, longitude, radius
            )
        elif all([min_lat, min_lon, max_lat, max_lon]):
            buildings = await building_repo.get_buildings_in_rectangle(
                db, min_lat, min_lon, max_lat, max_lon
            )
        else:
            raise ValueError(
                "Необходимо указать либо радиус, либо координаты прямоугольной области"
            )

        building_ids = [b.id for b in buildings]

        if not building_ids:
            return []

        query = (
            select(Organization)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
            )
            .where(Organization.building_id.in_(building_ids))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_activity_name(
        self, db: AsyncSession, activity_name: str, include_children: bool = True
    ) -> List[Organization]:
        from app.db.repositories.activity_repository import ActivityRepository

        activity_repo = ActivityRepository()

        activity = await activity_repo.get_by_name(db, activity_name)
        if not activity:
            return []

        if not include_children:
            query = (
                select(Organization)
                .options(
                    selectinload(Organization.building),
                    selectinload(Organization.phone_numbers),
                    selectinload(Organization.activities),
                )
                .where(Organization.activities.any(Activity.id == activity.id))
            )
            result = await db.execute(query)
            return result.scalars().all()

        activity_ids = await activity_repo.get_all_child_ids(db, activity.id)

        query = (
            select(Organization)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
            )
            .where(Organization.activities.any(Activity.id.in_(activity_ids)))
        )
        result = await db.execute(query)
        return result.scalars().all()
