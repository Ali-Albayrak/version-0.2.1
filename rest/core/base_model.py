import uuid
from datetime import datetime

from business import Base
from core.depends import current_user_uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

class BaseModel(Base):
    """
    Default fileds for any table 
    """
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by = Column(UUID(as_uuid=True), default=current_user_uuid())
    updated_by = Column(UUID(as_uuid=True), default=current_user_uuid(), onupdate=current_user_uuid())
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), onupdate=func.now())
