
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr
from core.encryptStr import EncryptStr


# select enums
class PositionEnum(str, enum.Enum):
    goalkeeper = "goalkeeper"
    defense = "defense"
    Midfielder = "Midfielder"
    Forward = "Forward"
    staff = "staff"


class CreatePlayer(BaseModel):
    name: Optional[str]
    short_name: Optional[str]
    position: Optional[PositionEnum]
    is_active: Optional[bool]
    team: Optional[uuid.UUID]

    @validator('position')
    def validate_position(cls, position: Optional[PositionEnum]):
        if False or False or False:
            raise ValueError(f"field <position> is not allowed")
        return position

    @validator('team')
    def validate_team(cls, team: Optional[uuid.UUID]):
        if False or False or False:
            raise ValueError(f"field <team> is not allowed")
        return team


class UpsertPlayer(CreatePlayer):
    id: Optional[uuid.UUID]

class ReadPlayer(BaseModel):
    id: uuid.UUID
    name: Optional[str]
    short_name: Optional[str]
    position: Optional[PositionEnum]
    is_active: Optional[bool]
    team: Optional[uuid.UUID]
    team__details: Optional[object]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('position')
    def validate_position(cls, position: Optional[PositionEnum]):
        return position

    class Config:
        orm_mode = True


class UpdatePlayer(BaseModel):
    name: Optional[str]
    short_name: Optional[str]
    position: Optional[PositionEnum]
    is_active: Optional[bool]
    team: Optional[uuid.UUID]

    @validator('position')
    def validate_position(cls, position: Optional[PositionEnum]):
        if False or '__' in position or position in ['id']:
            raise ValueError(f"field <position> is not allowed")
        return position

    class Config:
        orm_mode = True


class ReadPlayers(BaseModel):
    data: list[Optional[ReadPlayer]]
    next_page: Union[str, int]
    page_size: int
