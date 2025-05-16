from typing import List, Optional, Set
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.repositories.base_repository import BaseRepository
from app.db.models import Activity
from app.domain.models.activity import ActivityCreate, ActivityUpdate


class ActivityRepository(BaseRepository[Activity, ActivityCreate, ActivityUpdate]):

    def __init__(self):
        super().__init__(Activity)

    async def get_root_activities(self, db: AsyncSession) -> List[Activity]:
        query = (
            select(Activity)
            .where(Activity.parent_id.is_(None))
            .options(selectinload(Activity.children))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_children(
        self, db: AsyncSession, activity_id: int
    ) -> Optional[Activity]:
        query = (
            select(Activity)
            .options(selectinload(Activity.children))
            .where(Activity.id == activity_id)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_activity_tree(self, db: AsyncSession) -> List[Activity]:
        query = (
            select(Activity)
            .where(Activity.parent_id.is_(None))
            .options(selectinload(Activity.children))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_all_child_ids(self, db: AsyncSession, activity_id: int) -> Set[int]:
        result = {activity_id}

        query = select(Activity).where(Activity.parent_id == activity_id)
        db_result = await db.execute(query)
        children = db_result.scalars().all()

        for child in children:
            child_ids = await self.get_all_child_ids(db, child.id)
            result.update(child_ids)

        return result

    async def check_depth(self, db: AsyncSession, parent_id: Optional[int]) -> int:
        
        if parent_id is None:
            return 0

        depth = 1
        current_id = parent_id

        while current_id is not None:
            query = select(Activity.parent_id).where(Activity.id == current_id)
            result = await db.execute(query)
            parent_id = result.scalar_one_or_none()

            if parent_id is not None:
                depth += 1
                current_id = parent_id
            else:
                break

        return depth

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Activity]:
        query = select(Activity).where(func.lower(Activity.name) == func.lower(name))
        result = await db.execute(query)
        return result.scalars().first()

    async def search_by_name(self, db: AsyncSession, name: str) -> List[Activity]:
        query = select(Activity).where(
            func.lower(Activity.name).contains(func.lower(name))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: ActivityCreate
    ) -> Activity:
        obj_in_data = obj_in.model_dump()
        
        if "parent_id" in obj_in_data and obj_in_data["parent_id"] == 0:
            obj_in_data["parent_id"] = None
        
        db_obj = Activity(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
