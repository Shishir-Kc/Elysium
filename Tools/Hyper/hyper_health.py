import os 
import httpx
import asyncio
import logging




try:

 logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='Logs/Hyper/Hyper_status.log',
    filemode='a'
)
except Exception as e:
   print(f"Error {e}")   
logger = logging.getLogger(__name__)

async def hyper_server_status():
    
    async with httpx.AsyncClient() as client:
    
     response = await client.get('https://hyper-backend-8y8v.onrender.com/api/v1/')
     response = response.text
    logger.info(response)
    if not response:
        return False
    
    return True

if __name__ == "__main__":
   asyncio.run(hyper_server_status())