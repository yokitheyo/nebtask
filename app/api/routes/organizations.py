from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_async_session
from app.core.security import get_api_key
from app.api.dependencies import get_organization_service
from app.services.organization_service import OrganizationService
from app.domain.models.organization import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationWithActivities,
)
from app.domain.models.relations import OrganizationFull

router = APIRouter()


@router.get("/", response_model=List[Organization])
async def read_organizations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
    organization_service: OrganizationService = Depends(get_organization_service),
    api_key: str = Depends(get_api_key),
):
    
    organizations = await organization_service.get_all(db, skip=skip, limit=limit)
    return organizations


@router.post("/", response_model=Organization)
async def create_organization(
    organization: OrganizationCreate,
    db: AsyncSession = Depends(get_async_session),
    organization_service: OrganizationService = Depends(get_organization_service),
    api_key: str = Depends(get_api_key),
):
   
    db_organization = await organization_service.create(db=db, organization_in=organization)
    from app.domain.models.organization import Organization as OrganizationSchema
    return OrganizationSchema.model_validate(db_organization)


@router.get("/search", response_model=List[Organization])
async def search_organizations(
    name: Optional[str] = None,
    building_id: Optional[int] = None,
    activity_id: Optional[int] = None,
    activity_name: Optional[str] = None,
    include_child_activities: bool = True,
    db: AsyncSession = Depends(get_async_session),
    organization_service: OrganizationService = Depends(get_organization_service),
    api_key: str = Depends(get_api_key),
):
    
    if name:
        return await organization_service.search_by_name(db, name=name)
    elif building_id:
        return await organization_service.get_by_building(db, building_id=building_id)
    elif activity_id:
        return await organization_service.get_by_activity(
            db, activity_id=activity_id, include_children=include_child_activities
        )
    elif activity_name:
        return await organization_service.get_by_activity_name(
            db, activity_name=activity_name, include_children=include_child_activities
        )
    else:
        return await organization_service.get_all(db, skip=0, limit=100)


@router.get("/by-location", response_model=List[Organization])
async def get_organizations_by_location(
    latitude: float,
    longitude: float,
    radius: Optional[float] = None,
    min_lat: Optional[float] = None,
    min_lon: Optional[float] = None,
    max_lat: Optional[float] = None,
    max_lon: Optional[float] = None,
    db: AsyncSession = Depends(get_async_session),
    organization_service: OrganizationService = Depends(get_organization_service),
    api_key: str = Depends(get_api_key),
):
    
    try:
        return await organization_service.get_by_location(
            db,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            min_lat=min_lat,
            min_lon=min_lon,
            max_lat=max_lat,
            max_lon=max_lon,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{organization_id}", response_model=OrganizationFull)
async def read_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_async_session),
    organization_service: OrganizationService = Depends(get_organization_service),
    api_key: str = Depends(get_api_key),
):
    
    db_organization = await organization_service.get_with_details(
        db, organization_id=organization_id
    )
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return db_organization


@router.put("/{organization_id}", response_model=Organization)
async def update_organization(
    organization_id: int,
    organization: OrganizationUpdate,
    db: AsyncSession = Depends(get_async_session),
    organization_service: OrganizationService = Depends(get_organization_service),
    api_key: str = Depends(get_api_key),
):
    
    db_organization = await organization_service.update(
        db, organization_id=organization_id, organization_in=organization
    )
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    from app.domain.models.organization import Organization as OrganizationSchema
    return OrganizationSchema.model_validate(db_organization)


@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_async_session),
    organization_service: OrganizationService = Depends(get_organization_service),
    api_key: str = Depends(get_api_key),
):
    
    success = await organization_service.delete(db, organization_id=organization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return {"detail": "Организация успешно удалена"}
