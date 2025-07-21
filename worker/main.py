import asyncio
import os
from aiokafka import AIOKafkaConsumer
import json
from aiokafka.errors import GroupCoordinatorNotAvailableError, TopicAuthorizationFailedError, KafkaConnectionError, KafkaError

from shared.db.session import AsyncSessionLocal
from shared.db.crud import get_job, get_fingerprint  # <- добавили get_fingerprint
from browser_engine import run_scenario

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")

async def process_job(job_data):
    async with AsyncSessionLocal() as db:
        job = await get_job(db, job_data["job_id"])
        if not job:
            print(f"Job not found: {job_data['job_id']}")
            return
        fingerprint = await get_fingerprint(db, job.user_id)  # <-- получаем fingerprint
        await run_scenario(job, fingerprint)

async def connect_with_retries(consumer, max_retries=30, delay=10):
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries} to connect to Kafka at {KAFKA_BROKER}...")
            await consumer.start()
            print("Connected to Kafka and started consuming messages...")
            return True
        except (GroupCoordinatorNotAvailableError, TopicAuthorizationFailedError, KafkaConnectionError) as e:
            print(f"Kafka error (retrying): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            continue
        except KafkaError as e:
            print(f"General Kafka error: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            continue
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    return False

async def main():
    print("Starting Last User Engine worker...")
    consumer = AIOKafkaConsumer(
        'lastuser-tasks',
        bootstrap_servers=KAFKA_BROKER,
        group_id="lastuser-worker",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        max_poll_interval_ms=600000,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000
    )
    try:
        if not await connect_with_retries(consumer):
            raise Exception("Failed to connect to Kafka after retries")
        async for msg in consumer:
            print(f"Received message: {msg.value}")
            await process_job(msg.value)
    except Exception as e:
        print(f"Kafka connection error: {e}")
        raise
    finally:
        print("Stopping Kafka consumer...")
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())
