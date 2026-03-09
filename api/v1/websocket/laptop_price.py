from fastapi import FastAPI,WebSocket,APIRouter,WebSocketDisconnect
import random
import json
import asyncio


router = APIRouter()



@router.websocket('/ws/')
async def live_price_update(websocket:WebSocket):
    await websocket.accept()
    try:
     while True:
        dummy_price = {
        "product": "Laptop",
        "price": random.randint(000,999)
        } 

        await websocket.send_text(json.dumps(dummy_price))
        await asyncio.sleep(10)
    except WebSocketDisconnect:
       print("User Disconnected !")
           


    except Exception as e:
       print(f"idk something is not working out! {e} ")
