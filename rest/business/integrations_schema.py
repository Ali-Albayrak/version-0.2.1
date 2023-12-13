
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr


# select enums
class TypeEnum(Optional[str] = Field(default=None), enum.Enum):
    github = "github"
    smtp = "smtp"
    ses = "ses"
    facebook = "facebook"
    x = "x"
    google = "google"


class CreateIntegration(BaseModel):
    id: Optional[uuid.UUID]
    name: Optional[str] = Field(default=None)
    type: Optional[TypeEnum]
    creds: EncryptStr
    provider: Optional[uuid.UUID] = Field(default=None)

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        if False or False or False:
            raise ValueError(f"field <type> is not allowed")
        return type

    @validator('provider')
    def validate_provider(cls, provider: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <provider> is not allowed")
        return provider


class UpsertIntegration(CreateIntegration):
    id: uuid.UUID

class ReadIntegration(BaseModel):
    id: uuid.UUID
    name: Optional[str] = Field(default=None)
    type: Optional[TypeEnum]
    creds: str
    provider: Optional[uuid.UUID]
    provider__details: Optional[object]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        return type

    class Config:
        orm_mode = True


class UpdateIntegration(BaseModel):
    name: Optional[str] = Field(default=None)
    type: Optional[TypeEnum]
    creds: str
    provider: Optional[uuid.UUID] = Field(default=None)

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        if False or '__' in type or type in ['id']:
            raise ValueError(f"field <type> is not allowed")
        return type

    class Config:
        orm_mode = True


class ReadIntegrations(BaseModel):
    data: list[Optional[ReadIntegration]]
    next_page: Union[str, int]
    page_size: int
