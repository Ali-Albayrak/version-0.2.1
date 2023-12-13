
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr




class CreateRuntime_Variable(BaseModel):
    id: Optional[uuid.UUID]
    configs: EncryptStr
    is_active: Optional[bool] = Field(default=False)
    app: Optional[uuid.UUID] = Field(default=None)
    solution: Optional[uuid.UUID] = Field(default=None)

    @validator('app')
    def validate_app(cls, app: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <app> is not allowed")
        return app

    @validator('solution')
    def validate_solution(cls, solution: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <solution> is not allowed")
        return solution


class UpsertRuntime_Variable(CreateRuntime_Variable):
    id: uuid.UUID

class ReadRuntime_Variable(BaseModel):
    id: uuid.UUID
    configs: str
    is_active: Optional[bool] = Field(default=False)
    app: Optional[uuid.UUID]
    app__details: Optional[object]
    solution: Optional[uuid.UUID]
    solution__details: Optional[object]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    class Config:
        orm_mode = True


class UpdateRuntime_Variable(BaseModel):
    configs: str
    is_active: Optional[bool] = Field(default=False)
    app: Optional[uuid.UUID] = Field(default=None)
    solution: Optional[uuid.UUID] = Field(default=None)

    class Config:
        orm_mode = True


class ReadRuntime_Variables(BaseModel):
    data: list[Optional[ReadRuntime_Variable]]
    next_page: Union[str, int]
    page_size: int
