import os
import importlib

from actions import solution_version_create, solution_version_update


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
        new_data = await solution_version_create.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="create")
        return new_data


    async def pre_update(self, **kwargs) -> dict:
        jwt = kwargs.get("jwt", {})
        new_data = kwargs.get("new_data", {})
        old_data = kwargs.get("old_data", {})
        well_known_urls = kwargs.get("well_known_urls", {})
        new_data = await solution_version_update.handler(jwt=jwt, new_data=new_data, old_data=old_data, well_known_urls=well_known_urls, method="update")
        return new_data





# select enums


class Solution_VersionModel(BaseModel):
    __tablename__ = 'solution_versions'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    major_version = Column(Integer, nullable=False, default=False)
            
    minor_version = Column(Integer, nullable=False, default=False)
            
    version = Column(Text, nullable=False, default=False)
            
    snapshot = Column(JSON, nullable=True, default=False)
            
    public = Column(BOOLEAN, nullable=True, default=False)
            
    zdl = Column(JSON, nullable=True, default=False)
            
    release_notes = Column(Text, nullable=True, default=False)
            
    resources = Column(ARRAY(Text), nullable=True, default=False)
    
    
    solution = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".solutions.id"))
    solution__details = relationship("SolutionModel", back_populates='solution_versions', lazy='subquery')
         
    app_versions__solution_versions = relationship('App_Version__Solution_VersionModel', back_populates='solution_versions__details', lazy='subquery')
         
    deployments = relationship('DeploymentModel', back_populates='solution_version__details', lazy='subquery')
                
    is_sections = Column(BOOLEAN, nullable=True, default=True)

    @classmethod
    async def objects(cls, session):
        obj = await CustomManager.async_init(cls, session)
        return obj        

    @classmethod
    async def validate_unique_version_solution(cls, db, version, solution, id=None):
        query = select(cls).where(cls.version==version, cls.solution==solution)
        if id is not None:
            query = query.where(cls.id != id)
        result = await db.execute(query)
        existing_record = result.scalars().first()
        if existing_record:
            raise HTTPException(status_code=422, detail={
                "field_name": "version_solution",
                "message": f"version_solution should be unique"
            })
