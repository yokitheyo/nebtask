from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_async_session
from app.core.security import get_api_key
from app.services.building_service import BuildingService
from app.services.activity_service import ActivityService
from app.services.organization_service import OrganizationService


async def get_building_service() -> BuildingService:
    return BuildingService()


async def get_activity_service() -> ActivityService:
    return ActivityService()


async def get_organization_service() -> OrganizationService:
    return OrganizationService()
