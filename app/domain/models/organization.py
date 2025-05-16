from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.domain.models.activity import Activity


class PhoneNumberBase(BaseModel):
    number: str = Field(..., description="Номер телефона")


class PhoneNumberCreate(PhoneNumberBase):
    pass


class PhoneNumber(PhoneNumberBase):
    id: int = Field(..., description="Идентификатор номера телефона")
    organization_id: int = Field(..., description="Идентификатор организации")
    model_config = ConfigDict(from_attributes=True)


class OrganizationBase(BaseModel):
    name: str = Field(..., description="Название организации")
    building_id: int = Field(..., description="Идентификатор здания",gt=0)


class OrganizationCreate(OrganizationBase):
    phone_numbers: List[PhoneNumberCreate] = Field(
        default_factory=list, description="Список номеров телефонов"
    )
    activity_ids: List[int] = Field(
        default_factory=list, description="Список идентификаторов видов деятельности"
    )


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название организации")
    building_id: Optional[int] = Field(None, description="Идентификатор здания")
    phone_numbers: Optional[List[PhoneNumberCreate]] = Field(
        None, description="Список номеров телефонов"
    )
    activity_ids: Optional[List[int]] = Field(
        None, description="Список идентификаторов видов деятельности"
    )


class Organization(OrganizationBase):
    id: int = Field(..., description="Идентификатор организации")
    phone_numbers: List[PhoneNumber] = Field(
        default_factory=list, description="Список номеров телефонов"
    )
    model_config = ConfigDict(from_attributes=True)


class OrganizationWithActivities(Organization):
    activities: List[Activity] = Field(
        default_factory=list, description="Список видов деятельности"
    )
    model_config = ConfigDict(from_attributes=True)
