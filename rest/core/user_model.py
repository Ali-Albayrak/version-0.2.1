import uuid
from datetime import datetime

from sqlalchemy import Column, Text, String, DATETIME
from business import Base


class UserModel(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(Text, nullable=False)
    created_on = Column(DATETIME, default=datetime.now())
    updated_on = Column(DATETIME, default=datetime.now(), onupdate=datetime.now())
