import asyncio
import logging
from sqlalchemy import select
from shared.db.crud import get_job, get_fingerprint
from browser_engine import run_scenario
from shared.db.session import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_fingerprint(db, user_id):
    try:
        logger.info(f"Fetching fingerprint for user_id: {user_id}")
        if user_id is None:
            logger.warning("user_id is None, returning None")
            return None
        res = await db.execute(select(Fingerprint).where(Fingerprint.user_id == user_id))
        result = res.scalars().first()
        if result is None:
            logger.warning(f"No fingerprint found for user_id: {user_id}")
        return result
    except Exception as e:
        logger.error(f"Error fetching fingerprint for user_id {user_id}: {e}")
        raise

async def process_job(message):
    job_id = message.get('job_id')
    async with get_db() as db:
        job = await get_job(db, job_id)
        if job is None:
            logger.error(f"Job with id {job_id} not found")
            return
        if not hasattr(job, 'user_id') or job.user_id is None:
            logger.warning(f"Job with id {job_id} has no user_id, proceeding without fingerprint")
            fingerprint = None
        else:
            fingerprint = await get_fingerprint(db, job.user_id)
        try:
            await run_scenario(job, fingerprint)
        except Exception as e:
            logger.error(f"Error running scenario for job {job_id}: {e}")
            return