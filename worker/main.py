import asyncio
import logging
from sqlalchemy import select
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from shared.db.crud import get_job, get_fingerprint
from browser_engine import run_scenario
from shared.db.models import Fingerprint
from shared.db.session import get_db
from config import KAFKA_BROKER

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
        return None  # Return None instead of raising to prevent worker crash

async def process_job(message):
    try:
        job_id = message.get('job_id')
        if not job_id:
            logger.error("Received message without job_id")
            return
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
                logger.info(f"Successfully processed job {job_id}")
            except Exception as e:
                logger.error(f"Error running scenario for job {job_id}: {e}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

async def consume_jobs():
    try:
        consumer = AIOKafkaConsumer(
            'lastuser-tasks',
            bootstrap_servers=KAFKA_BROKER,
            group_id="worker-group",
            auto_offset_reset='earliest'
        )
        await consumer.start()
        logger.info("Kafka consumer started")
        async for message in consumer:
            try:
                message_value = message.value.decode('utf-8')
                message_data = json.loads(message_value)
                await process_job(message_data)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in Kafka message: {e}")
            except Exception as e:
                logger.error(f"Error processing Kafka message: {e}")
    except KafkaError as e:
        logger.error(f"Kafka consumer error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in consumer: {e}")
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")

async def main():
    while True:
        try:
            await consume_jobs()
        except Exception as e:
            logger.error(f"Consumer crashed: {e}. Restarting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())