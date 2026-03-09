import aiosmtplib
from email.message import EmailMessage

from Elysium_Config.Email.email_config import(
    SMTP_HOST,
    SMTP_PASS,
    SMTP_PORT,
    SMTP_USER
)





async def prepare_email(
   
        subject:str,
        reciver:str,
        content:str
) -> bool:
   
   """
    Args:
        subject : str = a proper subject for the recipient to look at 
        reciver:str = reciver email address eg: johndoe@gmail.com
        content:str = message meant to be sent to the user !
   
   """
   try:
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = reciver
    message["Subject"] = subject
    message.set_content(content)

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASS,
        start_tls=True,
    )

    return True

   except Exception as e:
        return False
   

