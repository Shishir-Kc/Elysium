from fastapi import FastAPI, WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.v1 import router
from assets.Elysium.start_up import  (
wakey_wakey,
sleppy_sleppy,
)
from services.Server_Dir_check.server_file_integrety import check_sys_dir
from fastapi.responses import HTMLResponse

@asynccontextmanager
async def Lifespan(elysium_server:FastAPI):
    await check_sys_dir()
    await wakey_wakey()
    yield
    await sleppy_sleppy()

elysium_server = FastAPI(
    description="Home Server",
    title="Elysium",
    version='0.0.1',
    docs_url='/',
    lifespan=Lifespan
)

elysium_server.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_credentials = True,
    allow_headers = ['*']
)

f"""

 ↱ {elysium_server.include_router(router,prefix="/api")}
 This right here is for V1 api only ! 

 """ 

# test/ dummy webhook for getting laptop price it will be removed !  

html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Laptop Price Tracker</title>

<style>
body{
    font-family: Arial, sans-serif;
    background:#f4f6f8;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}

.card{
    background:white;
    padding:30px;
    border-radius:10px;
    box-shadow:0 5px 20px rgba(0,0,0,0.1);
    width:350px;
    text-align:center;
}

.price{
    font-size:40px;
    color:#2ecc71;
    font-weight:bold;
}

.status{
    font-size:14px;
    color:#888;
}

.updated{
    margin-top:10px;
    font-size:12px;
}
</style>

</head>
<body>

<div class="card">

<h2>Laptop Price</h2>

<div class="price" id="price">Waiting...</div>

<div class="status" id="status">
Connecting to server...
</div>

<div class="updated" id="time"></div>

</div>


<script>

const priceElement = document.getElementById("price");
const statusElement = document.getElementById("status");
const timeElement = document.getElementById("time");

const socket = new WebSocket("http://127.0.0.1:8000/api/v1/ws/");


socket.onopen = () => {
    statusElement.innerText = "Connected";
};


socket.onmessage = (event) => {

    const data = JSON.parse(event.data);

    priceElement.innerText = "$" + data.price;

    timeElement.innerText =
        "Updated at: " + new Date().toLocaleTimeString();
};


socket.onerror = () => {
    statusElement.innerText = "Connection error";
};


socket.onclose = () => {
    statusElement.innerText = "Disconnected";
};

</script>

</body>
</html>


"""
@elysium_server.get('/price/')
async def html_page():
    return HTMLResponse(html)

