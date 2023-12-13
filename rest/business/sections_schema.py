
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr


# select enums
class TypeEnum(Optional[str] = Field(default=None), enum.Enum):
    data = "data"
    web = "web"
    actions = "actions"
    services = "services"
    variables = "variables"
    assets = "assets"
    templates = "templates"


class CreateSection(BaseModel):
    id: Optional[uuid.UUID]
    name: Optional[str] = Field(default=None)
    type: Optional[TypeEnum]
    zdl: Optional[dict] = Field(default={})
    options: Optional[dict] = Field(default={})
    description: Optional[str] = Field(default=None)
    app: Optional[uuid.UUID] = Field(default=None)

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        if False or False or False:
            raise ValueError(f"field <type> is not allowed")
        return type

    @validator('app')
    def validate_app(cls, app: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <app> is not allowed")
        return app


class UpsertSection(CreateSection):
    id: uuid.UUID

class ReadSection(BaseModel):
    id: uuid.UUID
    name: Optional[str] = Field(default=None)
    type: Optional[TypeEnum]
    zdl: Optional[dict] = Field(default={})
    options: Optional[dict] = Field(default={})
    description: Optional[str] = Field(default=None)
    app: Optional[uuid.UUID]
    app__details: Optional[object]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        return type

    class Config:
        orm_mode = True


class UpdateSection(BaseModel):
    name: Optional[str] = Field(default=None)
    type: Optional[TypeEnum]
    zdl: Optional[dict] = Field(default={})
    options: Optional[dict] = Field(default={})
    description: Optional[str] = Field(default=None)
    app: Optional[uuid.UUID] = Field(default=None)

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        if False or '__' in type or type in ['id']:
            raise ValueError(f"field <type> is not allowed")
        return type

    class Config:
        orm_mode = True


class ReadSections(BaseModel):
    data: list[Optional[ReadSection]]
    next_page: Union[str, int]
    page_size: int
