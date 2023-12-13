
from typing import Optional, Union, List
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr




class CreateApp_Version(BaseModel):
    id: Optional[uuid.UUID]
    major_version: Optional[int] = Field(default=None)
    minor_version: Optional[int] = Field(default=None)
    version: Optional[str] = Field(default=None)
    snapshot: Optional[dict] = Field(default={})
    zdl: Optional[dict] = Field(default={})
    public: Optional[bool] = Field(default=False)
    description: Optional[str] = Field(default=None)
    screenshots: Optional[List[Optional[uuid.UUID]]] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    owner: Optional[uuid.UUID] = Field(default=None)
    app: Optional[uuid.UUID] = Field(default=None)
    is_sections: Optional[bool] = Field(default=False)

    @validator('screenshots')
    def validate_screenshots(cls, screenshots: Optional[List[Optional[uuid.UUID]]] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <screenshots> is not allowed")
        if screenshots and len(screenshots) > 5:
            raise ValueError(f"field <screenshots> cannot exceed 5 charachters")
        return screenshots

    @validator('owner')
    def validate_owner(cls, owner: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <owner> is not allowed")
        return owner

    @validator('app')
    def validate_app(cls, app: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <app> is not allowed")
        return app


class UpsertApp_Version(CreateApp_Version):
    id: uuid.UUID

class ReadApp_Version(BaseModel):
    id: uuid.UUID
    major_version: Optional[int] = Field(default=None)
    minor_version: Optional[int] = Field(default=None)
    version: Optional[str] = Field(default=None)
    snapshot: Optional[dict] = Field(default={})
    zdl: Optional[dict] = Field(default={})
    public: Optional[bool] = Field(default=False)
    description: Optional[str] = Field(default=None)
    screenshots: Optional[List[Optional[uuid.UUID]]] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    owner: Optional[uuid.UUID]
    app: Optional[uuid.UUID]
    app__details: Optional[object]
    app_versions__solution_versions: Optional[list[object]]
    is_sections: Optional[bool] = Field(default=False)
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('screenshots')
    def validate_screenshots(cls, screenshots: Optional[List[Optional[uuid.UUID]]] = Field(default=None)):
        if screenshots and len(screenshots) > 5:
            raise ValueError(f"field <screenshots> cannot exceed 5 charachters")
        return screenshots

    class Config:
        orm_mode = True


class UpdateApp_Version(BaseModel):
    major_version: Optional[int] = Field(default=None)
    minor_version: Optional[int] = Field(default=None)
    version: Optional[str] = Field(default=None)
    snapshot: Optional[dict] = Field(default={})
    zdl: Optional[dict] = Field(default={})
    public: Optional[bool] = Field(default=False)
    description: Optional[str] = Field(default=None)
    screenshots: Optional[List[Optional[uuid.UUID]]] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    owner: Optional[uuid.UUID] = Field(default=None)
    app: Optional[uuid.UUID] = Field(default=None)
    app_versions__solution_versions: Optional[list[Union[str, dict, object]]]
    is_sections: Optional[bool] = Field(default=False)

    @validator('screenshots')
    def validate_screenshots(cls, screenshots: Optional[List[Optional[uuid.UUID]]] = Field(default=None)):
        if False or '__' in screenshots or screenshots in ['id']:
            raise ValueError(f"field <screenshots> is not allowed")
        if screenshots and len(screenshots) > 5:
            raise ValueError(f"field <screenshots> cannot exceed 5 charachters")
        return screenshots

    class Config:
        orm_mode = True


class ReadApp_Versions(BaseModel):
    data: list[Optional[ReadApp_Version]]
    next_page: Union[str, int]
    page_size: int
