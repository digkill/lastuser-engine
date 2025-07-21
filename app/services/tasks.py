import json
from kafka import KafkaProducer
from config import KAFKA_BROKER

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


async def create_job_in_db(db, campaign):
    pass


async def create_campaign(db, campaign):
    created_job_ids = []
    # Создаем jobs в БД и отправляем каждый в Kafka
    for _ in range(campaign.sessions):
        # Здесь создай запись в таблице jobs и получи job_id
        job_id = await create_job_in_db(db, campaign)  # напиши свою функцию или вставь свою логику создания
        producer.send('last user-tasks', {"job_id": job_id})
        created_job_ids.append(job_id)
    producer.flush()
    return created_job_ids

async def get_status(job_id):
    # Здесь ищи статус по job_id в БД
    return {"job_id": job_id, "status": "pending"}  # это просто пример
