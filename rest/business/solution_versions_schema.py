
from typing import Optional, Union, List
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr




class CreateSolution_Version(BaseModel):
    id: Optional[uuid.UUID]
    major_version: Optional[int] = Field(default=None)
    minor_version: Optional[int] = Field(default=None)
    version: Optional[str] = Field(default=None)
    snapshot: Optional[dict] = Field(default={})
    public: Optional[bool] = Field(default=False)
    zdl: Optional[dict] = Field(default={})
    release_notes: Optional[str] = Field(default=None)
    resources: Optional[List[Optional[str] = Field(default=None)]]
    solution: Optional[uuid.UUID] = Field(default=None)
    is_sections: Optional[bool] = Field(default=False)

    @validator('resources')
    def validate_resources(cls, resources: Optional[List[Optional[str] = Field(default=None)]]):
        if False or False or False:
            raise ValueError(f"field <resources> is not allowed")
        return resources

    @validator('solution')
    def validate_solution(cls, solution: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <solution> is not allowed")
        return solution


class UpsertSolution_Version(CreateSolution_Version):
    id: uuid.UUID

class ReadSolution_Version(BaseModel):
    id: uuid.UUID
    major_version: Optional[int] = Field(default=None)
    minor_version: Optional[int] = Field(default=None)
    version: Optional[str] = Field(default=None)
    snapshot: Optional[dict] = Field(default={})
    public: Optional[bool] = Field(default=False)
    zdl: Optional[dict] = Field(default={})
    release_notes: Optional[str] = Field(default=None)
    resources: Optional[List[Optional[str] = Field(default=None)]]
    solution: Optional[uuid.UUID]
    solution__details: Optional[object]
    app_versions__solution_versions: Optional[list[object]]
    deployments: Optional[list[object]]
    is_sections: Optional[bool] = Field(default=False)
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('resources')
    def validate_resources(cls, resources: Optional[List[Optional[str] = Field(default=None)]]):
        return resources

    class Config:
        orm_mode = True


class UpdateSolution_Version(BaseModel):
    major_version: Optional[int] = Field(default=None)
    minor_version: Optional[int] = Field(default=None)
    version: Optional[str] = Field(default=None)
    snapshot: Optional[dict] = Field(default={})
    public: Optional[bool] = Field(default=False)
    zdl: Optional[dict] = Field(default={})
    release_notes: Optional[str] = Field(default=None)
    resources: Optional[List[Optional[str] = Field(default=None)]]
    solution: Optional[uuid.UUID] = Field(default=None)
    app_versions__solution_versions: Optional[list[Union[str, dict, object]]]
    deployments: Optional[list[Union[str, dict, object]]]
    is_sections: Optional[bool] = Field(default=False)

    @validator('resources')
    def validate_resources(cls, resources: Optional[List[Optional[str] = Field(default=None)]]):
        if False or '__' in resources or resources in ['id']:
            raise ValueError(f"field <resources> is not allowed")
        return resources

    class Config:
        orm_mode = True


class ReadSolution_Versions(BaseModel):
    data: list[Optional[ReadSolution_Version]]
    next_page: Union[str, int]
    page_size: int
