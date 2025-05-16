from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class BuildingBase(BaseModel):
    name: str = Field(..., description="Название здания")
    address: str = Field(..., description="Адрес здания")
    latitude: float = Field(..., description="Широта")
    longitude: float = Field(..., description="Долгота")


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название здания")
    address: Optional[str] = Field(None, description="Адрес здания")
    latitude: Optional[float] = Field(None, description="Широта")
    longitude: Optional[float] = Field(None, description="Долгота")


class Building(BuildingBase):
    id: int = Field(..., description="Идентификатор здания")
    model_config = ConfigDict(from_attributes=True)
