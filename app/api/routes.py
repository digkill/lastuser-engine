from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json
import logging
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError  # Updated import

from shared.db.crud import (
    create_campaign, get_campaign, get_all_campaigns,
    create_job, get_job, get_jobs_by_campaign, get_all_jobs
)
from schemas import CampaignCreate, CampaignInfo, JobInfo
from shared.db.session import get_db
from config import KAFKA_BROKER

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize Kafka Producer with error handling
async def get_kafka_producer():
    """
    Provide an AIOKafkaProducer instance for dependency injection.

    Returns:
        AIOKafkaProducer: Kafka producer instance or None if connection fails.
    """
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retry_backoff_ms=500,
            request_timeout_ms=10000
        )
        await producer.start()
        return producer
    except KafkaError as e:
        logger.error(f"Failed to initialize Kafka producer: {e}")
        return None


router = APIRouter(prefix="/api", tags=["campaigns", "jobs"])


# --- CAMPAIGNS ---

@router.post("/campaigns/", response_model=CampaignInfo)
async def create_campaign_route(
        data: CampaignCreate,
        db: AsyncSession = Depends(get_db),
        producer: AIOKafkaProducer = Depends(get_kafka_producer)
):
    """
    Create a new campaign and associated jobs, sending job IDs to Kafka.

    Args:
        data: Campaign creation data including query, URL, and session count.
        db: Async database session.
        producer: Kafka producer instance.

    Returns:
        CampaignInfo: The created campaign details.

    Raises:
        HTTPException: If campaign creation fails or Kafka producer is unavailable.
    """
    try:
        campaign = await create_campaign(db, data.dict())
        # Create jobs and send to Kafka
        for _ in range(data.sessions):
            job = await create_job(db, campaign.id)
            if producer:
                try:
                    await producer.send_and_wait('lastuser-tasks', {"job_id": job.id})
                except KafkaError as e:
                    logger.error(f"Failed to send job {job.id} to Kafka: {e}")
            else:
                logger.warning(f"Kafka producer unavailable, skipping job {job.id}")
        return CampaignInfo.model_validate(campaign)
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail="Failed to create campaign")


@router.get("/campaigns/", response_model=List[CampaignInfo])
async def list_campaigns_route(db: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of all campaigns.

    Args:
        db: Async database session.

    Returns:
        List[CampaignInfo]: List of all campaigns.
    """
    try:
        campaigns = await get_all_campaigns(db)
        return [CampaignInfo.model_validate(c) for c in campaigns]
    except Exception as e:
        logger.error(f"Error fetching campaigns: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch campaigns")


@router.get("/campaigns/{campaign_id}", response_model=CampaignInfo)
async def get_campaign_route(
        campaign_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific campaign by ID.

    Args:
        campaign_id: ID of the campaign to retrieve.
        db: Async database session.

    Returns:
        CampaignInfo: Details of the requested campaign.

    Raises:
        HTTPException: If the campaign is not found.
    """
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
    """
    Retrieve a specific job by ID.

    Args:
        job_id: ID of the job to retrieve.
        db: Async database session.

    Returns:
        JobInfo: Details of the requested job.

    Raises:
        HTTPException: If the job is not found.
    """
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobInfo.model_validate(job)


@router.post("/jobs/{job_id}/run", response_model=JobInfo)
async def run_job_route(
        job_id: int,
        db: AsyncSession = Depends(get_db),
        producer: AIOKafkaProducer = Depends(get_kafka_producer)
):
    """
    Run a specific job by sending its ID to Kafka.

    Args:
        job_id: ID of the job to run.
        db: Async database session.
        producer: Kafka producer instance.

    Returns:
        JobInfo: Details of the job.

    Raises:
        HTTPException: If the job is not found or Kafka producer is unavailable.
    """
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if producer:
        try:
            await producer.send_and_wait('lastuser-tasks', {"job_id": job.id})
        except KafkaError as e:
            logger.error(f"Failed to send job {job_id} to Kafka: {e}")
            raise HTTPException(status_code=500, detail="Failed to send job to Kafka")
    else:
        logger.warning(f"Kafka producer unavailable, cannot send job {job_id}")
        raise HTTPException(status_code=503, detail="Kafka producer unavailable")
    return JobInfo.model_validate(job)


@router.get("/jobs/", response_model=List[JobInfo])
async def list_jobs_route(
        db: AsyncSession = Depends(get_db),
        campaign_id: Optional[int] = Query(None, description="Filter jobs by campaign ID")
):
    """
    Retrieve a list of jobs, optionally filtered by campaign ID.

    Args:
        db: Async database session.
        campaign_id: Optional campaign ID to filter jobs.

    Returns:
        List[JobInfo]: List of jobs.
    """
    try:
        if campaign_id:
            jobs = await get_jobs_by_campaign(db, campaign_id)
        else:
            jobs = await get_all_jobs(db)
        return [JobInfo.model_validate(j) for j in jobs]
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch jobs")