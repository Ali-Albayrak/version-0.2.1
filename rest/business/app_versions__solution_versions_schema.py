
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr




class CreateApp_Version__Solution_Version(BaseModel):
    id: Optional[uuid.UUID]
    solution_versions: Optional[uuid.UUID] = Field(default=None)
    app_versions: Optional[uuid.UUID] = Field(default=None)

    @validator('solution_versions')
    def validate_solution_versions(cls, solution_versions: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <solution_versions> is not allowed")
        return solution_versions

    @validator('app_versions')
    def validate_app_versions(cls, app_versions: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <app_versions> is not allowed")
        return app_versions


class UpsertApp_Version__Solution_Version(CreateApp_Version__Solution_Version):
    id: uuid.UUID

class ReadApp_Version__Solution_Version(BaseModel):
    id: uuid.UUID
    solution_versions: Optional[uuid.UUID]
    solution_versions__details: Optional[object]
    app_versions: Optional[uuid.UUID]
    app_versions__details: Optional[object]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    class Config:
        orm_mode = True


class UpdateApp_Version__Solution_Version(BaseModel):
    solution_versions: Optional[uuid.UUID] = Field(default=None)
    app_versions: Optional[uuid.UUID] = Field(default=None)

    class Config:
        orm_mode = True


class ReadApp_Versions__Solution_Versions(BaseModel):
    data: list[Optional[ReadApp_Version__Solution_Version]]
    next_page: Union[str, int]
    page_size: int
