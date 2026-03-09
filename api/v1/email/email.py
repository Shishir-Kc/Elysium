from fastapi import APIRouter
from Elysium_Celery.tasks import sending_mail
from Database.Schema.Email.email_schema import Email_Schema
router =  APIRouter()

@router.post("/send/email",tags=['send_email'])
def send_email_user(email:Email_Schema):
    try:
        sending_mail.delay(
        subject=email.subject,
        reciver=email.reciver,
        content=email.content
     )
        return {"status":"email_snd ! "}
    except:
        return {"status":"Failed"}
    