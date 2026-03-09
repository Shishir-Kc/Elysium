from langchain.tools import tool


@tool
def send_email(
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
   from Elysium_Celery.tasks import sending_mail
   

   response=sending_mail.delay(
      subject=subject,
        reciver=reciver,
        content=content
        )
   
   return {"id":response.id,"status":"email has been scheduled !"}