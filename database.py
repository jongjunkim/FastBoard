from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import aioredis

# Base for your models
Base = declarative_base()

# Asynchronous Engine
ASYNC_DATABASE_URL = "postgresql+asyncpg://developer:devpassword@127.0.0.1:25000/developer"
async_engine = create_async_engine(ASYNC_DATABASE_URL)

# Asynchronous SessionLocal
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, autocommit=False, autoflush=False)

async def get_async_db():
    db = AsyncSession(bind=async_engine, expire_on_commit=False)
    try:
        yield db
    finally:
        await db.close()

async def get_redis_connection():
    redis_conn = await aioredis.from_url(
       "redis://localhost:25100", 
        db=0,
        encoding="utf-8", 
        decode_responses=True
    )
    return redis_conn
