import os
import importlib




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import String, ForeignKey, Column
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select



# select enums


class App_Version__Solution_VersionModel(BaseModel):
    __tablename__ = 'app_versions__solution_versions'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

    
    
    solution_versions = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".solution_versions.id"))
    solution_versions__details = relationship("Solution_VersionModel", back_populates='app_versions__solution_versions', lazy='subquery')
        
    
    app_versions = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".app_versions.id"))
    app_versions__details = relationship("App_VersionModel", back_populates='app_versions__solution_versions', lazy='subquery')
    
    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj

