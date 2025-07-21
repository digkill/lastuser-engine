from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any

class CampaignCreate(BaseModel):
    name: str
    query: str
    url: str
    sessions: int = 10
    config: Optional[dict] = {}

class CampaignInfo(BaseModel):
    id: int
    name: str
    query: str
    url: str
    sessions: int
    config: dict
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class JobInfo(BaseModel):
    id: int
    campaign_id: int
    status: str
    started_at: Optional[str]
    finished_at: Optional[str]
    log: Optional[Any]
    updated_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class JobLogInfo(BaseModel):
    id: int
    job_id: int
    event: str
    message: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)

class ProxyInfo(BaseModel):
    id: int
    ip: str
    port: int
    login: str
    password: str
    type: str
    country: str
    status: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

class AntidetectProfileInfo(BaseModel):
    id: int
    external_id: str
    provider: str
    status: str
    last_used_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)
