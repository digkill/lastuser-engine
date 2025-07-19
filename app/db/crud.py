from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Campaign, Job, Proxy, AntidetectProfile

async def create_campaign(db: AsyncSession, data):
    campaign = Campaign(**data)
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign

async def get_campaign(db: AsyncSession, campaign_id):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    return result.scalars().first()

async def create_job(db: AsyncSession, campaign_id, status="new"):
    job = Job(campaign_id=campaign_id, status=status)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def get_job(db: AsyncSession, job_id):
    result = await db.execute(select(Job).where(Job.id == job_id))
    return result.scalars().first()
