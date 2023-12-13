
from typing import Optional, Union, List
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr


# select enums
class ChannelEnum(Optional[str] = Field(default=None), enum.Enum):
    email = "email"
    push = "push"
    mobile = "mobile"
    sms = "sms"


class CreateSolution_Template(BaseModel):
    id: Optional[uuid.UUID]
    template_name: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    body: Optional[str] = Field(default=None)
    required_params: Optional[List[Optional[str] = Field(default=None)]]
    channel: Optional[ChannelEnum]
    solution: Optional[uuid.UUID] = Field(default=None)

    @validator('required_params')
    def validate_required_params(cls, required_params: Optional[List[Optional[str] = Field(default=None)]]):
        if False or False or False:
            raise ValueError(f"field <required_params> is not allowed")
        return required_params

    @validator('channel')
    def validate_channel(cls, channel: Optional[ChannelEnum]):
        if False or False or False:
            raise ValueError(f"field <channel> is not allowed")
        return channel

    @validator('solution')
    def validate_solution(cls, solution: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <solution> is not allowed")
        return solution


class UpsertSolution_Template(CreateSolution_Template):
    id: uuid.UUID

class ReadSolution_Template(BaseModel):
    id: uuid.UUID
    template_name: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    body: Optional[str] = Field(default=None)
    required_params: Optional[List[Optional[str] = Field(default=None)]]
    channel: Optional[ChannelEnum]
    solution: Optional[uuid.UUID]
    solution__details: Optional[object]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('required_params')
    def validate_required_params(cls, required_params: Optional[List[Optional[str] = Field(default=None)]]):
        return required_params

    @validator('channel')
    def validate_channel(cls, channel: Optional[ChannelEnum]):
        return channel

    class Config:
        orm_mode = True


class UpdateSolution_Template(BaseModel):
    template_name: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    body: Optional[str] = Field(default=None)
    required_params: Optional[List[Optional[str] = Field(default=None)]]
    channel: Optional[ChannelEnum]
    solution: Optional[uuid.UUID] = Field(default=None)

    @validator('required_params')
    def validate_required_params(cls, required_params: Optional[List[Optional[str] = Field(default=None)]]):
        if False or '__' in required_params or required_params in ['id']:
            raise ValueError(f"field <required_params> is not allowed")
        return required_params

    @validator('channel')
    def validate_channel(cls, channel: Optional[ChannelEnum]):
        if False or '__' in channel or channel in ['id']:
            raise ValueError(f"field <channel> is not allowed")
        return channel

    class Config:
        orm_mode = True


class ReadSolution_Templates(BaseModel):
    data: list[Optional[ReadSolution_Template]]
    next_page: Union[str, int]
    page_size: int
