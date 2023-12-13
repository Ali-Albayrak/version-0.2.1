
from typing import Optional, Union, List
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr




class CreateDeployment(BaseModel):
    id: Optional[uuid.UUID]
    solution_name: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    completion_time: Optional[str] = Field(default=None)
    workflow_name: Optional[str] = Field(default=None)
    last_errors: Optional[List[Optional[str] = Field(default=None)]]
    secret: Optional[str] = Field(default=None)
    links: Optional[dict] = Field(default={})
    environment: Optional[uuid.UUID] = Field(default=None)
    solution_version: Optional[uuid.UUID] = Field(default=None)

    @validator('last_errors')
    def validate_last_errors(cls, last_errors: Optional[List[Optional[str] = Field(default=None)]]):
        if False or False or False:
            raise ValueError(f"field <last_errors> is not allowed")
        return last_errors

    @validator('environment')
    def validate_environment(cls, environment: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <environment> is not allowed")
        return environment

    @validator('solution_version')
    def validate_solution_version(cls, solution_version: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <solution_version> is not allowed")
        return solution_version


class UpsertDeployment(CreateDeployment):
    id: uuid.UUID

class ReadDeployment(BaseModel):
    id: uuid.UUID
    solution_name: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    completion_time: Optional[str] = Field(default=None)
    workflow_name: Optional[str] = Field(default=None)
    last_errors: Optional[List[Optional[str] = Field(default=None)]]
    secret: Optional[str] = Field(default=None)
    links: Optional[dict] = Field(default={})
    environment: Optional[uuid.UUID]
    environment__details: Optional[object]
    solution_version: Optional[uuid.UUID]
    solution_version__details: Optional[object]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('last_errors')
    def validate_last_errors(cls, last_errors: Optional[List[Optional[str] = Field(default=None)]]):
        return last_errors

    class Config:
        orm_mode = True


class UpdateDeployment(BaseModel):
    solution_name: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    completion_time: Optional[str] = Field(default=None)
    workflow_name: Optional[str] = Field(default=None)
    last_errors: Optional[List[Optional[str] = Field(default=None)]]
    secret: Optional[str] = Field(default=None)
    links: Optional[dict] = Field(default={})
    environment: Optional[uuid.UUID] = Field(default=None)
    solution_version: Optional[uuid.UUID] = Field(default=None)

    @validator('last_errors')
    def validate_last_errors(cls, last_errors: Optional[List[Optional[str] = Field(default=None)]]):
        if False or '__' in last_errors or last_errors in ['id']:
            raise ValueError(f"field <last_errors> is not allowed")
        return last_errors

    class Config:
        orm_mode = True


class ReadDeployments(BaseModel):
    data: list[Optional[ReadDeployment]]
    next_page: Union[str, int]
    page_size: int
