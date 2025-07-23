from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_DB_URL = os.getenv("DATABASE_URL")
if not DATABASE_DB_URL:
    raise RuntimeError("DATABASE_URL is not set in environment (.env)")
if not DATABASE_DB_URL.startswith("postgresql+asyncpg://"):
    raise ValueError("DATABASE_URL must use asyncpg driver (e.g., postgresql+asyncpg://...)")

engine = create_async_engine(DATABASE_DB_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session