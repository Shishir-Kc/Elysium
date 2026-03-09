from pydantic import BaseModel

class Email_Schema(BaseModel):
    subject:str
    reciver:str
    content:str