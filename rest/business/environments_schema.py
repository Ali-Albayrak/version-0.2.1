
from typing import Optional, Union
from typing import Union
import uuid
import enum
import datetime

from pydantic import BaseModel, validator, EmailStr, Field
from core.encryptStr import EncryptStr


# select enums
class CloudProviderEnum(Optional[str] = Field(default=None), enum.Enum):
    GCP = "GCP"
    AWS = "AWS"
    AZURE = "AZURE"
    ONPREM = "ONPREM"
# select enums
class KindEnum(Optional[str] = Field(default=None), enum.Enum):
    dev = "dev"
    prod = "prod"


class CreateEnvironment(BaseModel):
    id: Optional[uuid.UUID]
    name: Optional[str] = Field(default=None)
    cloud_provider: Optional[CloudProviderEnum]
    kind: Optional[KindEnum]
    cloud_creds: EncryptStr
    db_creds: EncryptStr
    project_id: Optional[str] = Field(default=None)
    region: Optional[str] = Field(default=None)
    domain: Optional[str] = Field(default=None)
    is_zek_domain: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)
    description: Optional[str] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    owner: Optional[uuid.UUID] = Field(default=None)

    @validator('cloud_provider')
    def validate_cloud_provider(cls, cloud_provider: Optional[CloudProviderEnum]):
        if False or False or False:
            raise ValueError(f"field <cloud_provider> is not allowed")
        return cloud_provider

    @validator('kind')
    def validate_kind(cls, kind: Optional[KindEnum]):
        if False or False or False:
            raise ValueError(f"field <kind> is not allowed")
        return kind

    @validator('owner')
    def validate_owner(cls, owner: Optional[uuid.UUID] = Field(default=None)):
        if False or False or False:
            raise ValueError(f"field <owner> is not allowed")
        return owner


class UpsertEnvironment(CreateEnvironment):
    id: uuid.UUID

class ReadEnvironment(BaseModel):
    id: uuid.UUID
    name: Optional[str] = Field(default=None)
    cloud_provider: Optional[CloudProviderEnum]
    kind: Optional[KindEnum]
    cloud_creds: str
    db_creds: str
    project_id: Optional[str] = Field(default=None)
    region: Optional[str] = Field(default=None)
    domain: Optional[str] = Field(default=None)
    is_zek_domain: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)
    description: Optional[str] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    owner: Optional[uuid.UUID]
    deployments: Optional[list[object]]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_on: datetime.datetime
    updated_on: datetime.datetime

    @validator('cloud_provider')
    def validate_cloud_provider(cls, cloud_provider: Optional[CloudProviderEnum]):
        return cloud_provider

    @validator('kind')
    def validate_kind(cls, kind: Optional[KindEnum]):
        return kind

    class Config:
        orm_mode = True


class UpdateEnvironment(BaseModel):
    name: Optional[str] = Field(default=None)
    cloud_provider: Optional[CloudProviderEnum]
    kind: Optional[KindEnum]
    cloud_creds: str
    db_creds: str
    project_id: Optional[str] = Field(default=None)
    region: Optional[str] = Field(default=None)
    domain: Optional[str] = Field(default=None)
    is_zek_domain: Optional[bool] = Field(default=False)
    is_active: Optional[bool] = Field(default=False)
    description: Optional[str] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    owner: Optional[uuid.UUID] = Field(default=None)
    deployments: Optional[list[Union[str, dict, object]]]

    @validator('cloud_provider')
    def validate_cloud_provider(cls, cloud_provider: Optional[CloudProviderEnum]):
        if False or '__' in cloud_provider or cloud_provider in ['id']:
            raise ValueError(f"field <cloud_provider> is not allowed")
        return cloud_provider

    @validator('kind')
    def validate_kind(cls, kind: Optional[KindEnum]):
        if False or '__' in kind or kind in ['id']:
            raise ValueError(f"field <kind> is not allowed")
        return kind

    class Config:
        orm_mode = True


class ReadEnvironments(BaseModel):
    data: list[Optional[ReadEnvironment]]
    next_page: Union[str, int]
    page_size: int
