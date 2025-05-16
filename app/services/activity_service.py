from typing import List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.activity_repository import ActivityRepository
from app.domain.models.activity import ActivityCreate, ActivityUpdate, Activity


class ActivityService:
    def __init__(self):
        self.repository = ActivityRepository()

    async def get(self, db: AsyncSession, activity_id: int) -> Optional[Activity]:
        return await self.repository.get(db, activity_id)

    async def get_with_children(
        self, db: AsyncSession, activity_id: int
    ) -> Optional[Activity]:
        return await self.repository.get_with_children(db, activity_id)

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Activity]:
        return await self.repository.get_multi(db, skip=skip, limit=limit)

    async def get_root_activities(self, db: AsyncSession) -> List[Activity]:
        return await self.repository.get_root_activities(db)

    async def get_activity_tree(self, db: AsyncSession) -> List[Activity]:
        return await self.repository.get_activity_tree(db)

    async def create(self, db: AsyncSession, activity_in: ActivityCreate) -> Activity:
        if activity_in.parent_id:
            depth = await self.repository.check_depth(db, activity_in.parent_id)
            if (
                depth >= 2
            ):  
                raise ValueError(
                    "Превышена максимальная глубина вложенности (3 уровня)"
                )

        return await self.repository.create(db, obj_in=activity_in)

    async def update(
        self, db: AsyncSession, activity_id: int, activity_in: ActivityUpdate
    ) -> Optional[Activity]:
        db_activity = await self.repository.get(db, activity_id)
        if not db_activity:
            return None

        if activity_in.parent_id and activity_in.parent_id == activity_id:
            raise ValueError(
                "Вид деятельности не может быть своим собственным родителем"
            )

        if activity_in.parent_id and activity_in.parent_id != db_activity.parent_id:
            depth = await self.repository.check_depth(db, activity_in.parent_id)
            if depth >= 2:
                raise ValueError(
                    "Превышена максимальная глубина вложенности (3 уровня)"
                )

            child_ids = await self.repository.get_all_child_ids(db, activity_id)
            if activity_in.parent_id in child_ids:
                raise ValueError("Обнаружена циклическая ссылка")

        return await self.repository.update(db, db_obj=db_activity, obj_in=activity_in)

    async def delete(self, db: AsyncSession, activity_id: int) -> bool:
        db_activity = await self.repository.remove(db, id=activity_id)
        return db_activity is not None

    async def get_all_child_ids(self, db: AsyncSession, activity_id: int) -> Set[int]:
        return await self.repository.get_all_child_ids(db, activity_id)
