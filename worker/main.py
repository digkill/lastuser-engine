import asyncio
from aiokafka import AIOKafkaConsumer
import json
from app.db.session import AsyncSessionLocal
from app.db.crud import get_job
from worker.browser_engine import run_scenario

KAFKA_BROKER = "kafka:9092"

async def process_job(job_data):
    async with AsyncSessionLocal() as db:
        job = await get_job(db, job_data["job_id"])
        if not job:
            print(f"Job not found: {job_data['job_id']}")
            return
        await run_scenario(job)

async def main():
    consumer = AIOKafkaConsumer(
        'lastuser-tasks',
        bootstrap_servers=KAFKA_BROKER,
        group_id="lastuser-worker",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )
    await consumer.start()
    try:
        async for msg in consumer:
            await process_job(msg.value)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())
