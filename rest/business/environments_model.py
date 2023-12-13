import os
import importlib




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import String, ForeignKey, Column, Text, BOOLEAN, Enum
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select



# select enums
class CloudProviderEnum(str, enum.Enum):
    GCP = "GCP"
    AWS = "AWS"
    AZURE = "AZURE"
    ONPREM = "ONPREM"
class KindEnum(str, enum.Enum):
    dev = "dev"
    prod = "prod"


class EnvironmentModel(BaseModel):
    __tablename__ = 'environments'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    name = Column(Text, nullable=False, default=False)
            
    cloud_provider = Column(Enum(CloudProviderEnum), nullable=False, default=False)
            
    kind = Column(Enum(KindEnum), nullable=False, default=False)
            
    cloud_creds = Column(Text, nullable=False, default=False)
            
    db_creds = Column(Text, nullable=False, default=False)
            
    project_id = Column(Text, nullable=False, default=False)
            
    region = Column(Text, nullable=False, default=False)
            
    domain = Column(Text, nullable=True, default=False)
            
    is_zek_domain = Column(BOOLEAN, nullable=False, default=True)
            
    is_active = Column(BOOLEAN, nullable=False, default=False)
            
    description = Column(Text, nullable=True, default=False)
            
    is_public = Column(BOOLEAN, nullable=True, default=False)
    
    
    owner = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))

         
    deployments = relationship('DeploymentModel', back_populates='environment__details', lazy='subquery')
    
    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj

    @classmethod
    async def validate_unique_name(cls, db, name, id=None):
        query = select(cls).where(cls.name==name)
        if id is not None:
            query = query.where(cls.id != id)
        existing_record = query.first()
        if existing_record:
            raise HTTPException(status_code=422, detail={
                "field_name": "name",
                "message": f"name should be unique"
            })
