import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.logger import log
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from mongosql import MongoSqlBase

Base = declarative_base(cls=(MongoSqlBase,))

DB_USERNAME = os.environ.get('DB_USERNAME', 'demo')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'demo29517')
DB_NAME = os.environ.get('DB_NAME', 'zekoder')
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', '26257')
DB_SYNC_DRIVER = os.environ.get('DB_DRIVER', 'postgresql+psycopg2')
DB_ASYNC_DRIVER = os.environ.get('DB_DRIVER', 'postgresql+asyncpg')
DB_SYNC_QUERY_PARAMS = os.environ.get('DB_SYNC_QUERY_PARAMS', 'sslmode=disable')
DB_ASYNC_QUERY_PARAMS = os.environ.get('DB_ASYNC_QUERY_PARAMS', 'ssl=disable')


db_async_url = f'{DB_ASYNC_DRIVER}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?{DB_ASYNC_QUERY_PARAMS}'
db_sync_url = f'{DB_SYNC_DRIVER}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?{DB_SYNC_QUERY_PARAMS}'

engine_args = {
                "pool_size": 10,
                "max_overflow": 5,
                "pool_timeout": 30,  # 30 seconds
                "pool_recycle": 3600,  # 1 hour
            }

engine_sync = create_engine(db_sync_url, echo=True, **engine_args)
db_sync_session: Session = sessionmaker(bind=engine_sync, expire_on_commit=False)


engine_async = create_async_engine(db_async_url, echo=True, **engine_args)
db_async_session: AsyncSession = sessionmaker(bind=engine_async, expire_on_commit=False, class_=AsyncSession)
