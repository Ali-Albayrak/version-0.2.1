import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.logger import log
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from mongosql import MongoSqlBase

Base = declarative_base(cls=(MongoSqlBase,))

# database credentials
DB_USERNAME = os.environ.get('DB_USERNAME', 'demo')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'demo29517')
DB_NAME = os.environ.get('DB_NAME', 'zekoder')
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', '26257')

# engine client config
DB_POOL_SIZE = os.environ.get('DB_POOL_SIZE', 10)
DB_MAX_OVERFLOW = os.environ.get('DB_POOL_SIZE', 5)
DB_POOL_TIMEOUT = os.environ.get('DB_POOL_SIZE', 30) #30 seconds
DB_POOL_RECYCLE = os.environ.get('DB_POOL_SIZE', 3600) #1 hour
DB_SYNC_DRIVER = os.environ.get('SYNC_DB_DRIVER', 'postgresql+psycopg2')
DB_ASYNC_DRIVER = os.environ.get('ASYNC_DB_DRIVER', 'postgresql+asyncpg')
SYNC_DB_QUERY_PARAMS = os.environ.get('SYNC_DB_QUERY_PARAMS', 'sslmode=disable')
ASYNC_DB_QUERY_PARAMS = os.environ.get('ASYNC_DB_QUERY_PARAMS', 'ssl=disable')

db_async_url = f'{DB_ASYNC_DRIVER}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?{ASYNC_DB_QUERY_PARAMS}'
db_sync_url = f'{DB_SYNC_DRIVER}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?{SYNC_DB_QUERY_PARAMS}'

engine_args = {
    "pool_size": DB_POOL_SIZE,
    "max_overflow": DB_MAX_OVERFLOW,
    "pool_timeout": DB_POOL_TIMEOUT,
    "pool_recycle": DB_POOL_RECYCLE,
}
engine_sync = create_engine(db_sync_url, echo=True, **engine_args)
db_sync_session: Session = sessionmaker(bind=engine_sync, expire_on_commit=False)
engine_async = create_async_engine(db_async_url, echo=True, **engine_args)
db_async_session: AsyncSession = sessionmaker(bind=engine_async, expire_on_commit=False, class_=AsyncSession)

