from typing import List
from pydantic import Field, ConfigDict, create_model

from app.domain.models.building import Building
from app.domain.models.organization import Organization, OrganizationBase, PhoneNumber
from app.domain.models.activity import Activity


BuildingWithOrganizations = create_model(
    "BuildingWithOrganizations",
    __base__=Building,
    organizations=(
        List[OrganizationBase],
        Field(default_factory=list, description="Список организаций"),
    ),
    __config__=ConfigDict(from_attributes=True),
)

OrganizationWithBuilding = create_model(
    "OrganizationWithBuilding",
    __base__=Organization,
    building=(Building, Field(..., description="Здание организации")),
    __config__=ConfigDict(from_attributes=True),
)

OrganizationFull = create_model(
    "OrganizationFull",
    id=(int, Field(..., description="Идентификатор организации")),
    name=(str, Field(..., description="Название организации")),
    phone_numbers=(
        List[PhoneNumber],
        Field(default_factory=list, description="Список номеров телефонов"),
    ),
    building=(Building, Field(..., description="Здание организации")),
    activities=(
        List[Activity],
        Field(default_factory=list, description="Список видов деятельности"),
    ),
    __config__=ConfigDict(from_attributes=True),
)

BuildingWithOrganizations.model_rebuild()
OrganizationWithBuilding.model_rebuild()
OrganizationFull.model_rebuild()
