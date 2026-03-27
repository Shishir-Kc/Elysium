import hashlib
import os
import json
import time
from pathlib import Path
import shutil
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Tools.Progress_bar.smooth_bar import smooth_progress


class Sentinel:
    def __init__(self) -> None:
        self.ignore_files = []
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.BACK_UP_DIR = f"{self.BASE_DIR}/Elysium_back_up"
        self.hasher = hashlib.sha256()
        self.Changed_files = []
        os.makedirs(
            f"{self.BASE_DIR}/Elysium_back_up", exist_ok=True
        )  # makes a dir named Elysium_back_up so that the current state of the code is saved in back up dir!
        self.current_hash = {}
        self.runtime_hash = {}
        self.is_run_time_hash = False

    def logo(self):
        with open("assets/Watcher/eye.txt", "r") as f:
            art = f.read()
        return art

    def hash_file(self, file_path):
        # print(file_path)
        self.hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                self.hasher.update(chunk)

        return self.hasher.hexdigest()

    def hash_directory(self, directory):
        self.hasher = hashlib.sha256()
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in self.ignore_files]

            for name in sorted(files):
                if name in self.ignore_files:
                    continue

                filepath = os.path.join(root, name)

                rel_path = os.path.relpath(filepath, directory)
                self.hasher.update(rel_path.encode())

                with open(filepath, "rb") as f:
                    while chunk := f.read(8192):
                        self.hasher.update(chunk)

        return self.hasher.hexdigest()

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

    def create_hash(self):
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
                    print(f"got an Error ! {e} {directory}")
            try:
                if os.path.isfile(full_dir):
                    self.current_hash[full_dir] = self.hash_file(full_dir)
                if os.path.isdir(full_dir):
                    self.current_hash[full_dir] = self.hash_directory(full_dir)
            except Exception as e:
                print(f"got an Error ! {e} {directory}")
        else:
            self.is_run_time_hash = True

    def create_back_up(self):
        smooth_progress(text="Creating Back Up ")
        for items in os.listdir(self.BASE_DIR):
            # print(items)
            src_path = os.path.join(self.BASE_DIR, items)
            destination_path = os.path.join(sentinel.BACK_UP_DIR, items)

            if os.path.basename(src_path) in sentinel.ignore_files:
                continue

            if os.path.isdir(src_path):
                try:
                    shutil.copytree(
                        src_path,
                        destination_path,
                        dirs_exist_ok=True,
                    )
                except Exception as e:
                    print(f"got an error ! {e}")
            else:
                shutil.copy2(src_path, destination_path)

    def watch(self):

        while True:
            _ = self.create_hash()

            if self.current_hash != self.runtime_hash:
                print("change detected in file . . . . ")
                print("Getting the file")
                for file_path in self.current_hash:
                    if self.current_hash[file_path] != self.runtime_hash[file_path]:
                        self.Changed_files.append(file_path)
                print("File(s) Changed at => ", self.Changed_files)
                break
            print("no change", end="\r", flush=True)
            time.sleep(5)


if __name__ == "__main__":
    sentinel = Sentinel()
    print(sentinel.logo())
    sentinel.load_ignore_file_names()
    sentinel.create_hash()
    sentinel.create_back_up()
    sentinel.watch()
