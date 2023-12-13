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


class App__SolutionModel(BaseModel):
    __tablename__ = 'apps__solutions'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

    
    
    solutions = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".solutions.id"))
    solutions__details = relationship("SolutionModel", back_populates='apps__solutions', lazy='subquery')
        
    
    apps = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".apps.id"))
    apps__details = relationship("AppModel", back_populates='apps__solutions', lazy='subquery')
    
    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj

