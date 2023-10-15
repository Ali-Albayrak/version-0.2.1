import os
import importlib




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import Enum, String, ForeignKey, Text, Column, BOOLEAN
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException



# select enums
class PositionEnum(str, enum.Enum):
    goalkeeper = "goalkeeper"
    defense = "defense"
    Midfielder = "Midfielder"
    Forward = "Forward"
    staff = "staff"


class PlayerModel(BaseModel):
    __tablename__ = 'players'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    name = Column(Text, nullable=True, default=None)
            
    short_name = Column(Text, nullable=True, default=None)
            
    position = Column(Enum(PositionEnum), nullable=True, default=None)
            
    is_active = Column(BOOLEAN, nullable=True, default=True)
    
    
    team = Column(String, ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".teams.id"))
    team__details = relationship("TeamModel", back_populates='players')
    
    @classmethod
    def objects(cls, session):
        return Manager(cls, session)

