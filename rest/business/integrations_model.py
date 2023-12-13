import os
import importlib




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import Enum, String, ForeignKey, Column, Text
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select



# select enums
class TypeEnum(str, enum.Enum):
    github = "github"
    smtp = "smtp"
    ses = "ses"
    facebook = "facebook"
    x = "x"
    google = "google"


class IntegrationModel(BaseModel):
    __tablename__ = 'integrations'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    name = Column(Text, nullable=False, default=False)
            
    type = Column(Enum(TypeEnum), nullable=False, default=False)
            
    creds = Column(Text, nullable=False, default=False)
    
    
    provider = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".providers.id"))
    provider__details = relationship("ProviderModel", back_populates='integrations', lazy='subquery')
    
    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj

    @classmethod
    async def validate_unique_name_provider(cls, db, name, provider, id=None):
        query = select(cls).where(cls.name==name, cls.provider==provider)
        if id is not None:
            query = query.where(cls.id != id)
        result = await db.execute(query)
        existing_record = result.scalars().first()
        if existing_record:
            raise HTTPException(status_code=422, detail={
                "field_name": "name_provider",
                "message": f"name_provider should be unique"
            })
