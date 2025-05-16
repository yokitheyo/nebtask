from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_async_session
from app.core.security import get_api_key
from app.api.dependencies import get_building_service
from app.services.building_service import BuildingService
from app.domain.models.building import Building, BuildingCreate, BuildingUpdate
from app.domain.models.relations import BuildingWithOrganizations

router = APIRouter()


@router.get("/", response_model=List[Building])
async def read_buildings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
    building_service: BuildingService = Depends(get_building_service),
    api_key: str = Depends(get_api_key),
):
    
    buildings = await building_service.get_all(db, skip=skip, limit=limit)
    return buildings


@router.post("/", response_model=Building)
async def create_building(
    building: BuildingCreate,
    db: AsyncSession = Depends(get_async_session),
    building_service: BuildingService = Depends(get_building_service),
    api_key: str = Depends(get_api_key),
):
    
    return await building_service.create(db=db, building_in=building)


@router.get("/{building_id}", response_model=BuildingWithOrganizations)
async def read_building(
    building_id: int,
    db: AsyncSession = Depends(get_async_session),
    building_service: BuildingService = Depends(get_building_service),
    api_key: str = Depends(get_api_key),
):
    
    db_building = await building_service.get_with_organizations(
        db, building_id=building_id
    )
    if db_building is None:
        raise HTTPException(status_code=404, detail="Здание не найдено")
    return db_building


@router.put("/{building_id}", response_model=Building)
async def update_building(
    building_id: int,
    building: BuildingUpdate,
    db: AsyncSession = Depends(get_async_session),
    building_service: BuildingService = Depends(get_building_service),
    api_key: str = Depends(get_api_key),
):
    
    db_building = await building_service.update(
        db, building_id=building_id, building_in=building
    )
    if db_building is None:
        raise HTTPException(status_code=404, detail="Здание не найдено")
    return db_building


@router.delete("/{building_id}")
async def delete_building(
    building_id: int,
    db: AsyncSession = Depends(get_async_session),
    building_service: BuildingService = Depends(get_building_service),
    api_key: str = Depends(get_api_key),
):
    
    success = await building_service.delete(db, building_id=building_id)
    if not success:
        raise HTTPException(status_code=404, detail="Здание не найдено")
    return {"detail": "Здание успешно удалено"}
