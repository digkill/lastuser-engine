from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud import create_campaign, get_campaign, create_job, get_job
from app.api.schemas import CampaignCreate, CampaignInfo, JobInfo
from app.db.session import get_db

router = APIRouter(prefix="/api")

@router.post("/campaigns/", response_model=CampaignInfo)
async def create_campaign_route(data: CampaignCreate, db: AsyncSession = Depends(get_db)):
    campaign = await create_campaign(db, data.dict())
    for _ in range(data.sessions):
        await create_job(db, campaign.id)
    return CampaignInfo.from_orm(campaign)

@router.get("/campaigns/{campaign_id}", response_model=CampaignInfo)
async def get_campaign_route(campaign_id: int, db: AsyncSession = Depends(get_db)):
    campaign = await get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignInfo.from_orm(campaign)

@router.get("/jobs/{job_id}", response_model=JobInfo)
async def get_job_route(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobInfo.from_orm(job)
