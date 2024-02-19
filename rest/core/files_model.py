import uuid
from datetime import datetime

from sqlalchemy import Column, String, DATETIME, INTEGER
from business import Base
from sqlalchemy.dialects.postgresql import UUID


class FilesModel(Base):
    __tablename__ = 'files'
    __table_args__ = {'schema': 'public'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    minio_address = Column(String, nullable=False) #is it uuid?
    minio_thumbnail_address = Column(String)
    width = Column(INTEGER)
    height = Column(INTEGER)
    tn_width = Column(INTEGER)
    tn_height = Column(INTEGER)
    file_size = Column(INTEGER, nullable=False)
    file_name = Column(String, nullable=False)
    file_extension = Column(String)
    file_description = Column(String)
    created_on = Column(DATETIME, default=datetime.now())
    updated_on = Column(DATETIME, default=datetime.now(), onupdate=datetime.now())
