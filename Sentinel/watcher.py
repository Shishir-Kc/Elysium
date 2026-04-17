import hashlib
import os
import json
import time
from pathlib import Path
import shutil
import sys
import logging
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tools.Progress_bar.smooth_bar import smooth_progress

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Sentinel")


class Sentinel:
    def __init__(self, watch_interval: int = 5) -> None:
        self.ignore_files: list[str] = []
        self.BASE_DIR: Path = Path(__file__).resolve().parent.parent
        self.BACK_UP_DIR: str = f"{self.BASE_DIR}/Elysium_back_up"
        self.Changed_files: list[str] = []
        self.watch_interval: int = watch_interval
        os.makedirs(f"{self.BASE_DIR}/Elysium_back_up", exist_ok=True)
        self.current_hash: dict[str, str] = {}
        self.runtime_hash: dict[str, str] = {}
        self.is_run_time_hash: bool = False

    def logo(self) -> str:
        with open("assets/Watcher/eye.txt", "r") as f:
            art = f.read()
        return art

    def hash_file(self, file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        return hasher.hexdigest()

    def hash_directory(self, directory: str) -> str:
        hasher = hashlib.sha256()
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in self.ignore_files]

            for name in sorted(files):
                if name in self.ignore_files:
                    continue

                filepath = os.path.join(root, name)

                rel_path = os.path.relpath(filepath, directory)
                hasher.update(rel_path.encode())

                with open(filepath, "rb") as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)

        return hasher.hexdigest()

    def load_ignore_file_names(self) -> list[str]:
        with open(
            f"{os.path.dirname(os.path.abspath(__file__))}/ignore.json", "r"
        ) as f:
            data = json.load(f)

        if isinstance(data, list):
            self.ignore_files = data
        else:
            for _, i in data.items():
                self.ignore_files.append(i)
        return self.ignore_files

    def create_hash(self) -> None:
        for directory in os.listdir(self.BASE_DIR):
            full_dir = os.path.join(self.BASE_DIR, directory)
            if os.path.basename(full_dir) in self.ignore_files:
                continue
            if not self.is_run_time_hash:
                try:
                    if os.path.isfile(full_dir):
                        self.runtime_hash[full_dir] = self.hash_file(full_dir)
                    if os.path.isdir(full_dir):
                        self.runtime_hash[full_dir] = self.hash_directory(full_dir)
                except Exception as e:
                    logger.error(f"Error hashing {directory}: {e}")
                    continue
            try:
                if os.path.isfile(full_dir):
                    self.current_hash[full_dir] = self.hash_file(full_dir)
                if os.path.isdir(full_dir):
                    self.current_hash[full_dir] = self.hash_directory(full_dir)
            except Exception as e:
                logger.error(f"Error hashing {directory}: {e}")
        self.is_run_time_hash = True

    def create_back_up(self) -> None:
        smooth_progress(text="Creating Back Up ")
        for items in os.listdir(self.BASE_DIR):
            src_path = os.path.join(self.BASE_DIR, items)
            destination_path = os.path.join(self.BACK_UP_DIR, items)

            if os.path.basename(src_path) in self.ignore_files:
                continue

            if os.path.isdir(src_path):
                try:
                    shutil.copytree(
                        src_path,
                        destination_path,
                        dirs_exist_ok=True,
                    )
                except Exception as e:
                    logger.error(f"Error backing up {items}: {e}")
            else:
                shutil.copy2(src_path, destination_path)

    def watch(self) -> None:
        logger.info("Starting watch mode")
        while True:
            _ = self.create_hash()

            if self.current_hash != self.runtime_hash:
                logger.warning("Change detected in files")
                for file_path in self.current_hash:
                    if self.current_hash[file_path] != self.runtime_hash[file_path]:
                        self.Changed_files.append(file_path)
                logger.info(f"File(s) changed at => {self.Changed_files}")
                break
            logger.debug("No change detected")
            time.sleep(self.watch_interval)


if __name__ == "__main__":
    sentinel = Sentinel()
    print(sentinel.logo())
    sentinel.load_ignore_file_names()
    sentinel.create_hash()
    sentinel.create_back_up()
    sentinel.watch()
