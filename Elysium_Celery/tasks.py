from Elysium_Celery.config import celery
from services.Email.email_service import prepare_email
import time
import asyncio

@celery.task(bind=True,max_retries=3)
def idk_man(self):
    time.sleep(1)

@celery.task
def sending_mail( subject:str,
        reciver:str,
        content:str):
    asyncio.run(prepare_email(
        subject=subject,
        reciver=reciver,
        content=content
    ))