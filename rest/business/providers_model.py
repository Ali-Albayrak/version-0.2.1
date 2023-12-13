import os
import importlib




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import String, ForeignKey, Column, Text, BOOLEAN
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select



# select enums


class ProviderModel(BaseModel):
    __tablename__ = 'providers'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    name = Column(Text, nullable=False, default=False)
            
    location = Column(Text, nullable=False, default=False)
            
    short_name = Column(Text, nullable=False, default=False)
            
    bio = Column(Text, nullable=True, default=False)
    
    
    owner = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))

        
    provider_image = Column(UUID(as_uuid=True), ForeignKey("public.files.id"))
                
    is_active = Column(BOOLEAN, nullable=True, default=False)
     
    solutions = relationship('SolutionModel', back_populates='provider__details', lazy='subquery')
         
    apps = relationship('AppModel', back_populates='provider__details', lazy='subquery')
         
    integrations = relationship('IntegrationModel', back_populates='provider__details', lazy='subquery')
    
    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj

    @classmethod
    async def validate_unique_short_name(cls, db, short_name, id=None):
        query = select(cls).where(cls.short_name==short_name)
        if id is not None:
            query = query.where(cls.id != id)
        result = await db.execute(query)
        existing_record = result.scalars().first()
        if existing_record:
            raise HTTPException(status_code=422, detail={
                "field_name": "short_name",
                "message": f"short_name should be unique"
            })
