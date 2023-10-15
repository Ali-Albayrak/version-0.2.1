
from typing import Optional, List
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr
from core.encryptStr import EncryptStr


# select enums
class TypeEnum(str, enum.Enum):
    covered = "covered"
    open = "open"


class CreateStadium(BaseModel):
    name: Optional[str]
    location: Optional[str]
    type: Optional[TypeEnum]
    capacity: Optional[int]
    profile_image: Optional[uuid.UUID]
    license_file: Optional[uuid.UUID]
    family: Optional[dict]
    preivous_teams: Optional[List[str]]
    birthdate: Optional[datetime.date]

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        if False or False or False:
            raise ValueError(f"field <type> is not allowed")
        return type

    @validator('preivous_teams')
    def validate_preivous_teams(cls, preivous_teams: Optional[List[str]]):
        if False or False or False:
            raise ValueError(f"field <preivous_teams> is not allowed")
        if preivous_teams and len(preivous_teams) > 5:
            raise ValueError(f"field <preivous_teams> cannot exceed 5 charachters")
        return preivous_teams


class UpsertStadium(CreateStadium):
    id: Optional[uuid.UUID]

class ReadStadium(BaseModel):
    id: uuid.UUID
    name: Optional[str]
    location: Optional[str]
    type: Optional[TypeEnum]
    capacity: Optional[int]
    profile_image: Optional[uuid.UUID]
    license_file: Optional[uuid.UUID]
    family: Optional[dict]
    preivous_teams: Optional[List[str]]
    birthdate: Optional[datetime.date]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        return type

    @validator('preivous_teams')
    def validate_preivous_teams(cls, preivous_teams: Optional[List[str]]):
        if preivous_teams and len(preivous_teams) > 5:
            raise ValueError(f"field <preivous_teams> cannot exceed 5 charachters")
        return preivous_teams

    class Config:
        orm_mode = True


class UpdateStadium(BaseModel):
    name: Optional[str]
    location: Optional[str]
    type: Optional[TypeEnum]
    capacity: Optional[int]
    profile_image: Optional[uuid.UUID]
    license_file: Optional[uuid.UUID]
    family: Optional[dict]
    preivous_teams: Optional[List[str]]
    birthdate: Optional[datetime.date]

    @validator('type')
    def validate_type(cls, type: Optional[TypeEnum]):
        if False or '__' in type or type in ['id']:
            raise ValueError(f"field <type> is not allowed")
        return type

    @validator('preivous_teams')
    def validate_preivous_teams(cls, preivous_teams: Optional[List[str]]):
        if False or '__' in preivous_teams or preivous_teams in ['id']:
            raise ValueError(f"field <preivous_teams> is not allowed")
        if preivous_teams and len(preivous_teams) > 5:
            raise ValueError(f"field <preivous_teams> cannot exceed 5 charachters")
        return preivous_teams

    class Config:
        orm_mode = True


class ReadStadiums(BaseModel):
    data: list[Optional[ReadStadium]]
    next_page: Union[str, int]
    page_size: int
