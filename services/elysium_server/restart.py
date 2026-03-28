import threading
import os
import sys
import time
from Tools.Progress_bar.smooth_bar import smooth_progress
import logging

logger = logging.getLogger("uvicorn.errors")


def restart_service():
    logger.warning("Rebooting The server . . . ")
    with open("assets/Elysium/restarting.txt", "r") as f:
        restart_text = f.read()

    print(restart_text)

    time.sleep(5)
    os.system("clear")

    os.execv(sys.executable, [sys.executable] + sys.argv)


def restart_elysium():

    server_restart = threading.Thread(target=restart_service)
    Smooth_bar = threading.Thread(target=smooth_progress, kwargs={"text": "Rebooting"})

    server_restart.start()
    time.sleep(1)
    Smooth_bar.start()

    server_restart.join()
    Smooth_bar.join()
