import os
import importlib




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import String, ForeignKey, Column, Text, ARRAY, Enum
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select



# select enums
class ChannelEnum(str, enum.Enum):
    email = "email"
    push = "push"
    mobile = "mobile"
    sms = "sms"


class Solution_TemplateModel(BaseModel):
    __tablename__ = 'solution_templates'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    template_name = Column(Text, nullable=False, default=False)
            
    title = Column(Text, nullable=True, default=False)
            
    body = Column(Text, nullable=False, default=False)
            
    required_params = Column(ARRAY(Text), nullable=True, default=False)
            
    channel = Column(Enum(ChannelEnum), nullable=False, default=False)
    
    
    solution = Column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".solutions.id"))
    solution__details = relationship("SolutionModel", back_populates='solution_templates', lazy='subquery')
    
    @classmethod
    async def objects(cls, session):
        obj = await Manager.async_init(cls, session)
        return obj

