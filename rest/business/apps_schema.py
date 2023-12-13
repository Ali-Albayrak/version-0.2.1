
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr




class CreateApp(BaseModel):
    id: Optional[uuid.UUID]
    name: Optional[str] = Field(default=None)
    short_name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    public: Optional[bool] = Field(default=False)
    logo: Optional[uuid.UUID] = Field(default=None)
    is_active: Optional[bool] = Field(default=False)
    provider: Optional[uuid.UUID] = Field(default=None)

    @validator('name')
    def validate_name(cls, name: Optional[str] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <name> is not allowed")
        if name and len(name) > 36:
            raise ValueError(f"field <name> cannot exceed 36 charachters")
        if name and len(name) < 3:
            raise ValueError(f"field <name> cannot be lesser than 3 charachters")
        return name

    @validator('short_name')
    def validate_short_name(cls, short_name: Optional[str] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <short_name> is not allowed")
        if short_name and len(short_name) > 36:
            raise ValueError(f"field <short_name> cannot exceed 36 charachters")
        if short_name and len(short_name) < 3:
            raise ValueError(f"field <short_name> cannot be lesser than 3 charachters")
        return short_name

    @validator('description')
    def validate_description(cls, description: Optional[str] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <description> is not allowed")
        if description and len(description) > 512:
            raise ValueError(f"field <description> cannot exceed 512 charachters")
        if description and len(description) < 24:
            raise ValueError(f"field <description> cannot be lesser than 24 charachters")
        return description

    @validator('provider')
    def validate_provider(cls, provider: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <provider> is not allowed")
        return provider


class UpsertApp(CreateApp):
    id: uuid.UUID

class ReadApp(BaseModel):
    id: uuid.UUID
    name: Optional[str] = Field(default=None)
    short_name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    public: Optional[bool] = Field(default=False)
    logo: Optional[uuid.UUID]
    is_active: Optional[bool] = Field(default=False)
    provider: Optional[uuid.UUID]
    provider__details: Optional[object]
    app_versions: Optional[list[object]]
    apps__solutions: Optional[list[object]]
    sections: Optional[list[object]]
    runtime_variables: Optional[list[object]]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('name')
    def validate_name(cls, name: Optional[str] = Field(default=None)):
        if name and len(name) > 36:
            raise ValueError(f"field <name> cannot exceed 36 charachters")
        if name and len(name) < 3:
            raise ValueError(f"field <name> cannot be lesser than 3 charachters")
        return name

    @validator('short_name')
    def validate_short_name(cls, short_name: Optional[str] = Field(default=None)):
        if short_name and len(short_name) > 36:
            raise ValueError(f"field <short_name> cannot exceed 36 charachters")
        if short_name and len(short_name) < 3:
            raise ValueError(f"field <short_name> cannot be lesser than 3 charachters")
        return short_name

    @validator('description')
    def validate_description(cls, description: Optional[str] = Field(default=None)):
        if description and len(description) > 512:
            raise ValueError(f"field <description> cannot exceed 512 charachters")
        if description and len(description) < 24:
            raise ValueError(f"field <description> cannot be lesser than 24 charachters")
        return description

    class Config:
        orm_mode = True


class UpdateApp(BaseModel):
    name: Optional[str] = Field(default=None)
    short_name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    public: Optional[bool] = Field(default=False)
    logo: Optional[uuid.UUID] = Field(default=None)
    is_active: Optional[bool] = Field(default=False)
    provider: Optional[uuid.UUID] = Field(default=None)
    app_versions: Optional[list[Union[str, dict, object]]]
    apps__solutions: Optional[list[Union[str, dict, object]]]
    sections: Optional[list[Union[str, dict, object]]]
    runtime_variables: Optional[list[Union[str, dict, object]]]

    @validator('name')
    def validate_name(cls, name: Optional[str] = Field(default=None)):
        if False or '__' in name or name in ['id']:
            raise ValueError(f"field <name> is not allowed")
        if name and len(name) > 36:
            raise ValueError(f"field <name> cannot exceed 36 charachters")
        if name and len(name) < 3:
           raise ValueError(f"field <name> cannot be lesser than 3 charachters")
        return name

    @validator('short_name')
    def validate_short_name(cls, short_name: Optional[str] = Field(default=None)):
        if False or '__' in short_name or short_name in ['id']:
            raise ValueError(f"field <short_name> is not allowed")
        if short_name and len(short_name) > 36:
            raise ValueError(f"field <short_name> cannot exceed 36 charachters")
        if short_name and len(short_name) < 3:
           raise ValueError(f"field <short_name> cannot be lesser than 3 charachters")
        return short_name

    @validator('description')
    def validate_description(cls, description: Optional[str] = Field(default=None)):
        if False or '__' in description or description in ['id']:
            raise ValueError(f"field <description> is not allowed")
        if description and len(description) > 512:
            raise ValueError(f"field <description> cannot exceed 512 charachters")
        if description and len(description) < 24:
           raise ValueError(f"field <description> cannot be lesser than 24 charachters")
        return description

    class Config:
        orm_mode = True


class ReadApps(BaseModel):
    data: list[Optional[ReadApp]]
    next_page: Union[str, int]
    page_size: int
