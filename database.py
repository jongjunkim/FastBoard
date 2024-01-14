from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

DATABASE_URL = "postgresql://developer:devpassword@127.0.0.1:25000/developer"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.create_all(bind=engine)

redis_host = "localhost"
redis_port = 25100
redis_db = 0

def get_redis_connection():
    redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    return redis_conn


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

