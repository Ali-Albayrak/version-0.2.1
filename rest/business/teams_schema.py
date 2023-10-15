
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr
from core.encryptStr import EncryptStr




class CreateTeam(BaseModel):
    name: str
    location: str
    short_name: str
    bio: Optional[str]
    owner: Optional[uuid.UUID]

    @validator('name')
    def validate_name(cls, name: str):
        if False or False or False:
            raise ValueError(f"field <name> is not allowed")
        if name and len(name) > 200:
            raise ValueError(f"field <name> cannot exceed 200 charachters")
        if name and len(name) < 2:
            raise ValueError(f"field <name> cannot be lesser than 2 charachters")
        return name

    @validator('location')
    def validate_location(cls, location: str):
        if False or False or False:
            raise ValueError(f"field <location> is not allowed")
        return location

    @validator('owner')
    def validate_owner(cls, owner: Optional[uuid.UUID]):
        if False or False or False:
            raise ValueError(f"field <owner> is not allowed")
        return owner


class UpsertTeam(CreateTeam):
    id: Optional[uuid.UUID]

class ReadTeam(BaseModel):
    id: uuid.UUID
    name: str
    location: str
    short_name: str
    bio: Optional[str]
    owner: Optional[uuid.UUID]
    players: Optional[list[object]]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('name')
    def validate_name(cls, name: str):
        if name and len(name) > 200:
            raise ValueError(f"field <name> cannot exceed 200 charachters")
        if name and len(name) < 2:
            raise ValueError(f"field <name> cannot be lesser than 2 charachters")
        return name

    @validator('location')
    def validate_location(cls, location: str):
        return location

    class Config:
        orm_mode = True


class UpdateTeam(BaseModel):
    name: str
    location: str
    short_name: str
    bio: Optional[str]
    owner: Optional[uuid.UUID]
    players: Optional[list[Union[str, dict, object]]]

    @validator('name')
    def validate_name(cls, name: str):
        if False or '__' in name or name in ['id']:
            raise ValueError(f"field <name> is not allowed")
        if name and len(name) > 200:
            raise ValueError(f"field <name> cannot exceed 200 charachters")
        if name and len(name) < 2:
           raise ValueError(f"field <name> cannot be lesser than 2 charachters")
        return name

    @validator('location')
    def validate_location(cls, location: str):
        if False or '__' in location or location in ['id']:
            raise ValueError(f"field <location> is not allowed")
        return location

    class Config:
        orm_mode = True


class ReadTeams(BaseModel):
    data: list[Optional[ReadTeam]]
    next_page: Union[str, int]
    page_size: int
