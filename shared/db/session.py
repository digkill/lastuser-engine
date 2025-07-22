from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment (.env)")
if not DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise ValueError("DATABASE_URL must use asyncpg driver (e.g., postgresql+asyncpg://...)")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """
    Provide an async database session for FastAPI dependency injection.

    Yields:
        AsyncSession: An async SQLAlchemy session.
    """
    async with AsyncSessionLocal() as session:
        yield session