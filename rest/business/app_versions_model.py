import os
import importlib

from actions import app_version_create, app_version_update


import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import String, ForeignKey, Column, Text, Integer, BOOLEAN, JSON, ARRAY
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select

class CustomManager(Manager):
    async def pre_save(self, **kwargs) -> dict:
        jwt = kwargs.get("jwt", {})
        new_data = kwargs.get("new_data", {})
        old_data = kwargs.get("old_data", {})
        well_known_urls = kwargs.get("well_known_urls", {})
        new_data = await app_version_create.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="create")
        return new_data


    async def pre_update(self, **kwargs) -> dict:
        jwt = kwargs.get("jwt", {})
        new_data = kwargs.get("new_data", {})
        old_data = kwargs.get("old_data", {})
        well_known_urls = kwargs.get("well_known_urls", {})
        new_data = await app_version_update.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="update")
        return new_data





# select enums


class App_VersionModel(BaseModel):
    __tablename__ = 'app_versions'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    major_version = Column(Integer, nullable=False, default=False)
            
    minor_version = Column(Integer, nullable=False, default=False)
            
    version = Column(Text, nullable=False, default=False)
            
    snapshot = Column(JSON, nullable=True, default=False)
            
    zdl = Column(JSON, nullable=True, default=False)
            
    public = Column(BOOLEAN, nullable=True, default=False)
            
    description = Column(Text, nullable=False, default=False)
            
    screenshots = Column(ARRAY(Text), nullable=True, default=False)
            
    notes = Column(Text, nullable=True, default=False)
    
    
    owner = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))

        
    
    app = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".apps.id"))
    app__details = relationship("AppModel", back_populates='app_versions', lazy='subquery')
         
    app_versions__solution_versions = relationship('App_Version__Solution_VersionModel', back_populates='app_versions__details', lazy='subquery')
                
    is_sections = Column(BOOLEAN, nullable=True, default=True)

    @classmethod
    async def objects(cls, session):
        obj = await CustomManager.async_init(cls, session)
        return obj        

    @classmethod
    async def validate_unique_version_app(cls, db, version, app, id=None):
        query = select(cls).where(cls.version==version, cls.app==app)
        if id is not None:
            query = query.where(cls.id != id)
        result = await db.execute(query)
        existing_record = result.scalars().first()
        if existing_record:
            raise HTTPException(status_code=422, detail={
                "field_name": "version_app",
                "message": f"version_app should be unique"
            })
