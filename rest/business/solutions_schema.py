
from typing import Optional, Union, List
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr




class CreateSolution(BaseModel):
    id: Optional[uuid.UUID]
    name: Optional[str] = Field(default=None)
    short_name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=False)
    logo: Optional[uuid.UUID] = Field(default=None)
    apps_versions: Optional[List[Optional[str] = Field(default=None)]]
    owner: Optional[uuid.UUID] = Field(default=None)
    provider: Optional[uuid.UUID] = Field(default=None)

    @validator('apps_versions')
    def validate_apps_versions(cls, apps_versions: Optional[List[Optional[str] = Field(default=None)]]):
        if False or False or False:
            raise ValueError(f"field <apps_versions> is not allowed")
        return apps_versions

    @validator('owner')
    def validate_owner(cls, owner: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <owner> is not allowed")
        return owner

    @validator('provider')
    def validate_provider(cls, provider: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <provider> is not allowed")
        return provider


class UpsertSolution(CreateSolution):
    id: uuid.UUID

class ReadSolution(BaseModel):
    id: uuid.UUID
    name: Optional[str] = Field(default=None)
    short_name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=False)
    logo: Optional[uuid.UUID]
    apps_versions: Optional[List[Optional[str] = Field(default=None)]]
    owner: Optional[uuid.UUID]
    provider: Optional[uuid.UUID]
    provider__details: Optional[object]
    apps__solutions: Optional[list[object]]
    solution_versions: Optional[list[object]]
    runtime_variables: Optional[list[object]]
    solution_templates: Optional[list[object]]
    solution_sections: Optional[list[object]]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('apps_versions')
    def validate_apps_versions(cls, apps_versions: Optional[List[Optional[str] = Field(default=None)]]):
        return apps_versions

    class Config:
        orm_mode = True


class UpdateSolution(BaseModel):
    name: Optional[str] = Field(default=None)
    short_name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=False)
    logo: Optional[uuid.UUID] = Field(default=None)
    apps_versions: Optional[List[Optional[str] = Field(default=None)]]
    owner: Optional[uuid.UUID] = Field(default=None)
    provider: Optional[uuid.UUID] = Field(default=None)
    apps__solutions: Optional[list[Union[str, dict, object]]]
    solution_versions: Optional[list[Union[str, dict, object]]]
    runtime_variables: Optional[list[Union[str, dict, object]]]
    solution_templates: Optional[list[Union[str, dict, object]]]
    solution_sections: Optional[list[Union[str, dict, object]]]

    @validator('apps_versions')
    def validate_apps_versions(cls, apps_versions: Optional[List[Optional[str] = Field(default=None)]]):
        if False or '__' in apps_versions or apps_versions in ['id']:
            raise ValueError(f"field <apps_versions> is not allowed")
        return apps_versions

    class Config:
        orm_mode = True


class ReadSolutions(BaseModel):
    data: list[Optional[ReadSolution]]
    next_page: Union[str, int]
    page_size: int
