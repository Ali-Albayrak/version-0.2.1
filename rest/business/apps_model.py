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


class AppModel(BaseModel):
    __tablename__ = 'apps'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    name = Column(Text, nullable=False, default=False)
            
    short_name = Column(Text, nullable=False, default=False)
            
    description = Column(Text, nullable=False, default=False)
            
    status = Column(Text, nullable=True, default=False)
            
    public = Column(BOOLEAN, nullable=True, default=False)
    
    logo = Column(UUID(as_uuid=True), ForeignKey("public.files.id"))
                
    is_active = Column(BOOLEAN, nullable=True, default=False)
    
    
    provider = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".providers.id"))
    provider__details = relationship("ProviderModel", back_populates='apps', lazy='subquery')
         
    app_versions = relationship('App_VersionModel', back_populates='app__details', lazy='subquery')
         
    apps__solutions = relationship('App__SolutionModel', back_populates='apps__details', lazy='subquery')
         
    sections = relationship('SectionModel', back_populates='app__details', lazy='subquery')
         
    runtime_variables = relationship('Runtime_VariableModel', back_populates='app__details', lazy='subquery')
    
    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj

    @classmethod
    async def validate_unique_short_name(cls, db, short_name, id=None):
        query = select(cls).where(cls.short_name==short_name)
        if id is not None:
            query = query.where(cls.id != id)
        existing_record = query.first()
        if existing_record:
            raise HTTPException(status_code=422, detail={
                "field_name": "short_name",
                "message": f"short_name should be unique"
            })
