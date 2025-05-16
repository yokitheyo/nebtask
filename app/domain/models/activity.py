from typing import List, Optional
from pydantic import BaseModel, Field


class ActivityBase(BaseModel):
    name: str = Field(..., description="Название вида деятельности")
    parent_id: Optional[int] = Field(None, description="ID родительского вида деятельности")


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название вида деятельности")
    parent_id: Optional[int] = Field(None, description="ID родительского вида деятельности")


class Activity(ActivityBase):
    id: int = Field(..., description="Идентификатор вида деятельности")

    class Config:
        from_attributes = True


class ActivityWithChildren(Activity):
    children: List["ActivityWithChildren"] = Field(default_factory=list, description="Дочерние виды деятельности")

    class Config:
        from_attributes = True


ActivityWithChildren.model_rebuild()


class ActivityTree(BaseModel):
    activities: List[ActivityWithChildren] = Field(..., description="Список корневых видов деятельности")
