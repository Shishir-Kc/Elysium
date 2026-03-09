from server_logging import logger
import os 
import asyncio
from Tools.Progress_bar.smooth_bar import smooth_progress

async def wakey_wakey():
    smooth_progress(3,text="Booting")
    with open('assets/Elysium/branding.txt','r') as elysium:
        logo = elysium.read()
        print (logo)

async def sleppy_sleppy():
    with open('assets/Elysium/shutdown.txt','r') as elysium:
        logo = elysium.read()
        print (logo)
async def  startup_shutdown():
    wakey_wakey()
    await asyncio.sleep(5)
    sleppy_sleppy()



if __name__ == "__main__":
    asyncio.run(startup_shutdown())