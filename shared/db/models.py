from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Text, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql.sqltypes import DateTime  # Правильный импорт DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.sql import func

Base = declarative_base()

class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    query = Column(String(255))
    url = Column(String(255))
    sessions = Column(Integer)
    config = Column(JSON)
    created_at = Column(TIMESTAMP)

    jobs = relationship("Job", back_populates="campaign")

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    status = Column(String(32), default='new')
    started_at = Column(TIMESTAMP)
    finished_at = Column(TIMESTAMP)
    worker_id = Column(String(128))
    proxy_id = Column(Integer)
    profile_id = Column(Integer)
    log = Column(JSON)
    updated_at = Column(TIMESTAMP)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="jobs")
    campaign = relationship("Campaign", back_populates="jobs")
    logs = relationship("JobLog", back_populates="job")

class JobLog(Base):
    __tablename__ = 'job_logs'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    event = Column(String(255))
    message = Column(Text)
    created_at = Column(TIMESTAMP)

    job = relationship("Job", back_populates="logs")

class Proxy(Base):
    __tablename__ = 'proxies'
    id = Column(Integer, primary_key=True)
    ip = Column(String(64))
    port = Column(Integer)
    login = Column(String(128))
    password = Column(String(128))
    type = Column(String(16))
    country = Column(String(64))
    status = Column(String(32), default='active')
    updated_at = Column(TIMESTAMP)

class AntidetectProfile(Base):
    __tablename__ = 'antidetect_profiles'
    id = Column(Integer, primary_key=True)
    external_id = Column(String(128))
    provider = Column(String(32))
    status = Column(String(32), default='active')
    last_used_at = Column(TIMESTAMP)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    username = Column(String(64))
    role = Column(String(32))
    created_at = Column(TIMESTAMP)

    jobs = relationship("Job", back_populates="user")

class Fingerprint(Base):
    __tablename__ = 'fingerprints'
    id = Column(Integer, primary_key=True)
    label = Column(String(128), nullable=True)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, nullable=True)  # Если добавили user_id
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
