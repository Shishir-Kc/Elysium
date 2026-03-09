from celery import Celery

celery = Celery(
    __name__,
    backend='redis://127.0.0.1:6379',
    broker='redis://127.0.0.1:6379',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


celery.autodiscover_tasks(['Elysium_Celery'])
