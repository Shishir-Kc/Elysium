import logging

logging.basicConfig(
    level=logging.__all__,
    filename='Logs/Elysium/elysium.log',
    filemode='a'
)
logger= logging.getLogger("uvicorn.errors")
