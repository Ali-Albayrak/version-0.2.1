
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr


# select enums
class TypeEnum(Optional[str] = Field(default=None), enum.Enum):
    security = "security"


class CreateSolution_Section(BaseModel):
    id: Optional[uuid.UUID]
    name: Optional[str] = Field(default=None)
    type: Optional[TypeEnum]
    zdl: Optional[dict] = Field(default={})
    options: Optional[dict] = Field(default={})
    description: Optional[str] = Field(default=None)
    solution: Optional[uuid.UUID] = Field(default=None)

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        if False or False or False:
            raise ValueError(f"field <type> is not allowed")
        return type

    @validator('solution')
    def validate_solution(cls, solution: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <solution> is not allowed")
        return solution


class UpsertSolution_Section(CreateSolution_Section):
    id: uuid.UUID

class ReadSolution_Section(BaseModel):
    id: uuid.UUID
    name: Optional[str] = Field(default=None)
    type: Optional[TypeEnum]
    zdl: Optional[dict] = Field(default={})
    options: Optional[dict] = Field(default={})
    description: Optional[str] = Field(default=None)
    solution: Optional[uuid.UUID]
    solution__details: Optional[object]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        return type

    class Config:
        orm_mode = True


class UpdateSolution_Section(BaseModel):
    name: Optional[str] = Field(default=None)
    type: Optional[TypeEnum]
    zdl: Optional[dict] = Field(default={})
    options: Optional[dict] = Field(default={})
    description: Optional[str] = Field(default=None)
    solution: Optional[uuid.UUID] = Field(default=None)

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        if False or '__' in type or type in ['id']:
            raise ValueError(f"field <type> is not allowed")
        return type

    class Config:
        orm_mode = True


class ReadSolution_Sections(BaseModel):
    data: list[Optional[ReadSolution_Section]]
    next_page: Union[str, int]
    page_size: int
