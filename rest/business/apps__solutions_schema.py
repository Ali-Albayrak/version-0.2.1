
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr




class CreateApp__Solution(BaseModel):
    id: Optional[uuid.UUID]
    solutions: Optional[uuid.UUID] = Field(default=None)
    apps: Optional[uuid.UUID] = Field(default=None)

    @validator('solutions')
    def validate_solutions(cls, solutions: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <solutions> is not allowed")
        return solutions

    @validator('apps')
    def validate_apps(cls, apps: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <apps> is not allowed")
        return apps


class UpsertApp__Solution(CreateApp__Solution):
    id: uuid.UUID

class ReadApp__Solution(BaseModel):
    id: uuid.UUID
    solutions: Optional[uuid.UUID]
    solutions__details: Optional[object]
    apps: Optional[uuid.UUID]
    apps__details: Optional[object]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    class Config:
        orm_mode = True


class UpdateApp__Solution(BaseModel):
    solutions: Optional[uuid.UUID] = Field(default=None)
    apps: Optional[uuid.UUID] = Field(default=None)

    class Config:
        orm_mode = True


class ReadApps__Solutions(BaseModel):
    data: list[Optional[ReadApp__Solution]]
    next_page: Union[str, int]
    page_size: int
