import os
from celery import Celery
from celery.signals import worker_process_init
from app.nlp_engine import load_all_models

broker_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")

celery_instance = Celery(
    "nlp_worker",
    broker=broker_url,
    include=['app.tasks']
)

@worker_process_init.connect
def init_worker(**kwargs):
    """
    Runs exactly once when the Celery worker spawns.
    Used to load heavy ML models globally into memory.
    """
    load_all_models()
