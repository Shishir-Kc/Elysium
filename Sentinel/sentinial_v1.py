import hashlib
import os
import json

import time
from pathlib import Path
import shutil


def compute_has(file_path):
    with open(file_path, "rb") as f:
        file = f.read()
        return hashlib.sha256(file).hexdigest()


def look_dir():
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/dir.json", "r") as f:
        file = json.load(f)
    return file


BASE_DIR = Path(__file__).resolve().parent.parent

base_hash = compute_has(f"{BASE_DIR}/main.py")

os.makedirs(f"{BASE_DIR}/Elysium_back_up", exist_ok=True)

shutil.copy(f"{BASE_DIR}/*", f"{BASE_DIR}/Elysium_back_up/")

while True:
    current_hash = compute_has(f"{BASE_DIR}/main.py")
    if current_hash != base_hash:
        print("chage in file !")
        print("Rebooting the server ! ")
        break
    time.sleep(5)
