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

async def get_all_campaigns(db: AsyncSession):
    result = await db.execute(select(Campaign))
    return result.scalars().all()

async def get_jobs_by_campaign(db: AsyncSession, campaign_id: int):
    result = await db.execute(
        select(Job).where(Job.campaign_id == campaign_id)
    )
    return result.scalars().all()

async def get_all_jobs(db: AsyncSession):
    result = await db.execute(select(Job))
    return result.scalars().all()

async def get_fingerprint(db, user_id):
    res = await db.execute(select(Fingerprint).where(Fingerprint.user_id == user_id))
    fp = res.scalar_one_or_none()
    return fp.data if fp else None