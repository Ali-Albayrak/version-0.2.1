import os
import importlib

from actions import deploy_solution


import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import String, ForeignKey, Column, Text, JSON, ARRAY
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select

class CustomManager(Manager):

    async def post_save(self, **kwargs) -> dict:
        jwt = kwargs.get("jwt", {})
        new_data = kwargs.get("new_data", {})
        old_data = kwargs.get("old_data", {})
        well_known_urls = kwargs.get("well_known_urls", {})
        new_data = await deploy_solution.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="create")
        return new_data






# select enums


class DeploymentModel(BaseModel):
    __tablename__ = 'deployments'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    solution_name = Column(Text, nullable=False, default=False)
            
    status = Column(Text, nullable=True, default=False)
            
    completion_time = Column(Text, nullable=True, default=False)
            
    workflow_name = Column(Text, nullable=True, default=False)
            
    last_errors = Column(ARRAY(Text), nullable=True, default=False)
            
    secret = Column(Text, nullable=True, default=False)
            
    links = Column(JSON, nullable=True, default=False)
    
    
    environment = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".environments.id"))
    environment__details = relationship("EnvironmentModel", back_populates='deployments', lazy='subquery')
        
    
    solution_version = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".solution_versions.id"))
    solution_version__details = relationship("Solution_VersionModel", back_populates='deployments', lazy='subquery')
    
    @classmethod
    async def objects(cls, session):
        obj = await CustomManager.async_init(cls, session)
        return obj        

