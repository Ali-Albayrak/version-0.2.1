import os




import enum
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import Enum, Text, Integer, JSON, DATE, Column, ARRAY
from sqlalchemy.orm import relationship
from core.base_model import BaseModel
from core.manager import Manager
from fastapi import HTTPException



# select enums
class TypeEnum(str, enum.Enum):
    covered = "covered"
    open = "open"


class StadiumModel(BaseModel):
    __tablename__ = 'stadiums'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

            
    name = Column(Text, nullable=True, default=None)
            
    location = Column(Text, nullable=True, default=None)
            
    type = Column(Enum(TypeEnum), nullable=True, default=None)
            
    capacity = Column(Integer, nullable=True, default=None)
    
    profile_image = Column(String, ForeignKey("public.files.id"))
        
    license_file = Column(String, ForeignKey("public.files.id"))
                
    family = Column(JSON, nullable=True, default=None)
            
    preivous_teams = Column(ARRAY(Text), nullable=True, default=None)
            
    birthdate = Column(DATE, nullable=True, default=None)

    @classmethod
    def objects(cls, session):
        return Manager(cls, session)

    @classmethod
    def validate_unique_name_location(cls, db, name, location, id=None):
        query = db.query(cls).filter_by(name=name, location=location)
        if id is not None:
            query = query.filter(cls.id != id)
        existing_record = query.first()
        if existing_record:
            raise HTTPException(status_code=422, detail={
                "field_name": "name_location",
                "message": f"name_location should be unique"
            })
