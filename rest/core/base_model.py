import uuid
from datetime import datetime

from business import Base
from core.depends import current_user_uuid
from sqlalchemy import Column, String, DATETIME


class BaseModel(Base):
    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by = Column(String, default=current_user_uuid)
    updated_by = Column(String, default=current_user_uuid, onupdate=current_user_uuid)
    created_on = Column(DATETIME, default=datetime.now())
    updated_on = Column(DATETIME, default=datetime.now(), onupdate=datetime.now())
