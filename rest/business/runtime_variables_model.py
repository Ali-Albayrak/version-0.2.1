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


class Runtime_VariableModel(BaseModel):
    __tablename__ = 'runtime_variables'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    configs = Column(Text, nullable=False, default=False)
            
    is_active = Column(BOOLEAN, nullable=False, default=False)
    
    
    app = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".apps.id"))
    app__details = relationship("AppModel", back_populates='runtime_variables', lazy='subquery')
        
    
    solution = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".solutions.id"))
    solution__details = relationship("SolutionModel", back_populates='runtime_variables', lazy='subquery')
    
    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj

    @classmethod
    async def validate_unique_app_solution(cls, db, app, solution, id=None):
        query = select(cls).where(cls.app==app, cls.solution==solution)
        if id is not None:
            query = query.where(cls.id != id)
        result = await db.execute(query)
        existing_record = result.scalars().first()
        if existing_record:
            raise HTTPException(status_code=422, detail={
                "field_name": "app_solution",
                "message": f"app_solution should be unique"
            })
