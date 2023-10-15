import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.logger import log

from mongosql import MongoSqlBase

Base = declarative_base(cls=(MongoSqlBase,))

DB_USERNAME = os.environ.get('DB_USERNAME', 'demo')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'demo29517')
DB_NAME = os.environ.get('DB_NAME', 'zekoder')
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', '26257')
DB_DRIVER = os.environ.get('DB_DRIVER', 'postgresql+psycopg2')
DB_QUERY_PARAMS = os.environ.get('DB_QUERY_PARAMS', 'sslmode=require&sslrootcert=/tmp/demo2408646734/ca.crt')
db_url = f'{DB_DRIVER}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?{DB_QUERY_PARAMS}'
engine = create_engine(db_url)
db_session = sessionmaker(bind=engine, autoflush=False)
