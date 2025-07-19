import uuid
import json
from kafka import KafkaProducer
from app.config import KAFKA_BROKER

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

async def create_campaign(campaign):
    task_id = str(uuid.uuid4())
    # Один task — одна сессия, делаем пачку
    for _ in range(campaign.sessions):
        producer.send('lastuser-tasks', {
            "task_id": task_id,
            "query": campaign.query,
            "url": campaign.url,
        })
    producer.flush()
    return task_id

async def get_status(task_id):
    # Заглушка — в проде ищем в БД/кеше
    return {"task_id": task_id, "status": "pending"}
