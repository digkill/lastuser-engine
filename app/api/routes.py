from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import Query
from typing import List, Optional

from shared.db.crud import (
    create_campaign, get_campaign, get_all_campaigns,
    create_job, get_job, get_jobs_by_campaign, get_all_jobs
)
from schemas import CampaignCreate, CampaignInfo, JobInfo
from shared.db.session import get_db

import json
from kafka import KafkaProducer
from config import KAFKA_BROKER

# --- Kafka Producer ---
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

router = APIRouter(prefix="/api")

# --- CAMPAIGNS ---

@router.post("/campaigns/", response_model=CampaignInfo)
async def create_campaign_route(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db)
):
    campaign = await create_campaign(db, data.dict())
    # Для каждого job создаём запись и отправляем job_id в Kafka
    for _ in range(data.sessions):
        job = await create_job(db, campaign.id)
        producer.send('lastuser-tasks', {"job_id": job.id})
    producer.flush()
    return CampaignInfo.model_validate(campaign)

@router.get("/campaigns/", response_model=List[CampaignInfo])
async def list_campaigns_route(db: AsyncSession = Depends(get_db)):
    """Список всех кампаний (для фронта)"""
    campaigns = await get_all_campaigns(db)
    return [CampaignInfo.model_validate(c) for c in campaigns]

@router.get("/campaigns/{campaign_id}", response_model=CampaignInfo)
async def get_campaign_route(
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    campaign = await get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignInfo.model_validate(campaign)

# --- JOBS ---

@router.get("/jobs/{job_id}", response_model=JobInfo)
async def get_job_route(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobInfo.model_validate(job)

@router.post("/jobs/{job_id}/run", response_model=JobInfo)
async def run_job_route(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Отправка задания в Kafka (повторно или вручную)
    producer.send('lastuser-tasks', {"job_id": job.id})
    producer.flush()
    return JobInfo.model_validate(job)

@router.get("/jobs/", response_model=List[JobInfo])
async def list_jobs_route(
    db: AsyncSession = Depends(get_db),
    campaign_id: int = Query(None)   # <-- теперь не required!
):
    if campaign_id:
        jobs = await get_jobs_by_campaign(db, campaign_id)
    else:
        jobs = await get_all_jobs(db)
    return [JobInfo.model_validate(j) for j in jobs]
