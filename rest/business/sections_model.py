import os
import importlib




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import String, ForeignKey, Column, Text, JSON, Enum
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select



# select enums
class TypeEnum(str, enum.Enum):
    data = "data"
    web = "web"
    actions = "actions"
    services = "services"
    variables = "variables"
    assets = "assets"
    templates = "templates"


class SectionModel(BaseModel):
    __tablename__ = 'sections'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    name = Column(Text, nullable=True, default=False)
            
    type = Column(Enum(TypeEnum), nullable=False, default=False)
            
    zdl = Column(JSON, nullable=True, default=False)
            
    options = Column(JSON, nullable=True, default=False)
            
    description = Column(Text, nullable=True, default=False)
    
    
    app = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".apps.id"))
    app__details = relationship("AppModel", back_populates='sections', lazy='subquery')
    
    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj

    @classmethod
    async def validate_unique_type_app(cls, db, type, app, id=None):
        query = select(cls).where(cls.type==type, cls.app==app)
        if id is not None:
            query = query.where(cls.id != id)
        result = await db.execute(query)
        existing_record = result.scalars().first()
        if existing_record:
            raise HTTPException(status_code=422, detail={
                "field_name": "type_app",
                "message": f"type_app should be unique"
            })
