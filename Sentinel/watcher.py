import hashlib
import os
import json

import time
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
os.makedirs(f"{BASE_DIR}/Elysium_back_up", exist_ok=True)

shutil.copy(f"{BASE_DIR}/main.py", f"{BASE_DIR}/Elysium_back_up/")


class Sentinel:
    def __init__(self) -> None:
        self.ignore_files = []

    def compute_has(self, file_path):
        with open(file_path, "rb") as f:
            file = f.read()
        return hashlib.sha256(file).hexdigest()

    def look_dir(self):
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/dir.json", "r") as f:
            file = json.load(f)
            return file

    def load_ignore_file_names(self):

        with open(
            f"{os.path.dirname(os.path.abspath(__file__))}/ignore.json", "r"
        ) as f:
            data = json.load(f)

        for _, i in data.items():
            self.ignore_files.append(i)
        return self.ignore_files


sentinel = Sentinel()
base_hash = sentinel.compute_has(f"{BASE_DIR}/main.py")

print(sentinel.load_ignore_file_names())


def main():
    while True:
        current_hash = sentinel.compute_has(f"{BASE_DIR}/main.py")
        if current_hash != base_hash:
            print("chage in file !")
            print("Rebooting the server ! ")
            break
        time.sleep(5)


source = BASE_DIR
src_path = None


for items in os.listdir(source):
    # print(items)
    src_path = os.path.join(source, items)
    if os.path.basename(src_path) in sentinel.ignore_files:
        print(f"found => {src_path}")
