import os
import json
import asyncio
from dotenv import load_dotenv

from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

# Загрузка .env
load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise Exception("DATABASE_URL not set in .env")

# Создание асинхронного движка
engine = create_async_engine(db_url, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class Fingerprint(Base):
    __tablename__ = "fingerprints"
    id = Column(Integer, primary_key=True)
    label = Column(String(128))
    data = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

async def main():
    # Чтение JSON файла
    FINGERPRINTS_PATH = "./fingerprints.json"
    with open(FINGERPRINTS_PATH, "r", encoding="utf-8") as f:
        fingerprint = json.load(f)  # Это ДИКТ, не список!

    # Формирование label
    label = (
        fingerprint.get("label")
        or (fingerprint.get("platform") if isinstance(fingerprint.get("platform"), str) else None)
        or (fingerprint.get("vendor") if isinstance(fingerprint.get("vendor"), str) else None)
        or "imported"
    )

    # Асинхронная сессия
    async with AsyncSessionLocal() as session:
        obj = Fingerprint(label=label, data=fingerprint)
        session.add(obj)
        await session.commit()
        print("Импортирован 1 fingerprint!")

# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())