from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_async_session
from app.core.security import get_api_key
from app.api.dependencies import get_activity_service
from app.services.activity_service import ActivityService
from app.domain.models.activity import Activity, ActivityCreate, ActivityUpdate, ActivityWithChildren

router = APIRouter()


@router.get("/", response_model=List[Activity])
async def read_activities(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_async_session),
    activity_service: ActivityService = Depends(get_activity_service),
    api_key: str = Depends(get_api_key)
):
   
    activities = await activity_service.get_all(db, skip=skip, limit=limit)
    return activities


@router.post("/", response_model=Activity)
async def create_activity(
    activity: ActivityCreate, 
    db: AsyncSession = Depends(get_async_session),
    activity_service: ActivityService = Depends(get_activity_service),
    api_key: str = Depends(get_api_key)
):
    
    try:
        return await activity_service.create(db=db, activity_in=activity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{activity_id}", response_model=Activity)
async def read_activity(
    activity_id: int, 
    db: AsyncSession = Depends(get_async_session),
    activity_service: ActivityService = Depends(get_activity_service),
    api_key: str = Depends(get_api_key)
):
    
    db_activity = await activity_service.get(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Вид деятельности не найден")
    return db_activity


@router.put("/{activity_id}", response_model=Activity)
async def update_activity(
    activity_id: int, 
    activity: ActivityUpdate, 
    db: AsyncSession = Depends(get_async_session),
    activity_service: ActivityService = Depends(get_activity_service),
    api_key: str = Depends(get_api_key)
):
    
    try:
        db_activity = await activity_service.update(db, activity_id=activity_id, activity_in=activity)
        if db_activity is None:
            raise HTTPException(status_code=404, detail="Вид деятельности не найден")
        return db_activity
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: int, 
    db: AsyncSession = Depends(get_async_session),
    activity_service: ActivityService = Depends(get_activity_service),
    api_key: str = Depends(get_api_key)
):
   
    success = await activity_service.delete(db, activity_id=activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Вид деятельности не найден")
    return {"detail": "Вид деятельности успешно удален"}
