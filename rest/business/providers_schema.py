
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr




class CreateProvider(BaseModel):
    id: Optional[uuid.UUID]
    name: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    short_name: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    owner: Optional[uuid.UUID] = Field(default=None)
    provider_image: Optional[uuid.UUID] = Field(default=None)
    is_active: Optional[bool] = Field(default=False)

    @validator('name')
    def validate_name(cls, name: Optional[str] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <name> is not allowed")
        if name and len(name) > 30:
            raise ValueError(f"field <name> cannot exceed 30 charachters")
        if name and len(name) < 3:
            raise ValueError(f"field <name> cannot be lesser than 3 charachters")
        return name

    @validator('location')
    def validate_location(cls, location: Optional[str] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <location> is not allowed")
        if location and len(location) > 3:
            raise ValueError(f"field <location> cannot exceed 3 charachters")
        if location and len(location) < 3:
            raise ValueError(f"field <location> cannot be lesser than 3 charachters")
        return location

    @validator('short_name')
    def validate_short_name(cls, short_name: Optional[str] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <short_name> is not allowed")
        if short_name and len(short_name) > 36:
            raise ValueError(f"field <short_name> cannot exceed 36 charachters")
        if short_name and len(short_name) < 3:
            raise ValueError(f"field <short_name> cannot be lesser than 3 charachters")
        return short_name

    @validator('owner')
    def validate_owner(cls, owner: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <owner> is not allowed")
        return owner


class UpsertProvider(CreateProvider):
    id: uuid.UUID

class ReadProvider(BaseModel):
    id: uuid.UUID
    name: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    short_name: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    owner: Optional[uuid.UUID]
    provider_image: Optional[uuid.UUID]
    is_active: Optional[bool] = Field(default=False)
    solutions: Optional[list[object]]
    apps: Optional[list[object]]
    integrations: Optional[list[object]]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('name')
    def validate_name(cls, name: Optional[str] = Field(default=None)):
        if name and len(name) > 30:
            raise ValueError(f"field <name> cannot exceed 30 charachters")
        if name and len(name) < 3:
            raise ValueError(f"field <name> cannot be lesser than 3 charachters")
        return name

    @validator('location')
    def validate_location(cls, location: Optional[str] = Field(default=None)):
        if location and len(location) > 3:
            raise ValueError(f"field <location> cannot exceed 3 charachters")
        if location and len(location) < 3:
            raise ValueError(f"field <location> cannot be lesser than 3 charachters")
        return location

    @validator('short_name')
    def validate_short_name(cls, short_name: Optional[str] = Field(default=None)):
        if short_name and len(short_name) > 36:
            raise ValueError(f"field <short_name> cannot exceed 36 charachters")
        if short_name and len(short_name) < 3:
            raise ValueError(f"field <short_name> cannot be lesser than 3 charachters")
        return short_name

    class Config:
        orm_mode = True


class UpdateProvider(BaseModel):
    name: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    short_name: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    owner: Optional[uuid.UUID] = Field(default=None)
    provider_image: Optional[uuid.UUID] = Field(default=None)
    is_active: Optional[bool] = Field(default=False)
    solutions: Optional[list[Union[str, dict, object]]]
    apps: Optional[list[Union[str, dict, object]]]
    integrations: Optional[list[Union[str, dict, object]]]

    @validator('name')
    def validate_name(cls, name: Optional[str] = Field(default=None)):
        if False or '__' in name or name in ['id']:
            raise ValueError(f"field <name> is not allowed")
        if name and len(name) > 30:
            raise ValueError(f"field <name> cannot exceed 30 charachters")
        if name and len(name) < 3:
           raise ValueError(f"field <name> cannot be lesser than 3 charachters")
        return name

    @validator('location')
    def validate_location(cls, location: Optional[str] = Field(default=None)):
        if False or '__' in location or location in ['id']:
            raise ValueError(f"field <location> is not allowed")
        if location and len(location) > 3:
            raise ValueError(f"field <location> cannot exceed 3 charachters")
        if location and len(location) < 3:
           raise ValueError(f"field <location> cannot be lesser than 3 charachters")
        return location

    @validator('short_name')
    def validate_short_name(cls, short_name: Optional[str] = Field(default=None)):
        if False or '__' in short_name or short_name in ['id']:
            raise ValueError(f"field <short_name> is not allowed")
        if short_name and len(short_name) > 36:
            raise ValueError(f"field <short_name> cannot exceed 36 charachters")
        if short_name and len(short_name) < 3:
           raise ValueError(f"field <short_name> cannot be lesser than 3 charachters")
        return short_name

    class Config:
        orm_mode = True


class ReadProviders(BaseModel):
    data: list[Optional[ReadProvider]]
    next_page: Union[str, int]
    page_size: int
