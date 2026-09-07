""" This files contains comamnds for E.L.Y.S.I.U.M that is accessable by romeo       """

import json
from pathlib import Path

from elysium_config.path_config import show_elysium_paths
from elysium_config.updater import Updater
from linux.system import Linux
from logger_config import set_up_logger

logger = set_up_logger(name="Commands.elysium_info")

linux = Linux()

HOMEDIR = Path.home()
configdata = show_elysium_paths(all=True).get("elysium",{})
configpath = HOMEDIR/ ".E.L.Y.S.I.U.M"/ configdata.get("config",{})


def readconfig():
    with open(configpath,"r") as file:
        data = json.load(file)
    return data.get("elysium",{})



def version(args=None):
    version = readconfig().get("version",{})
    logger.info(f"Version : {version}")
    return version

def status(args=None):
    status = readconfig().get("status",{})
    logger.info(f"Status : {status}")
    return status

def last_development_changes(args=None):
    dev = readconfig().get("last_development_changes",{}) 
    logger.info(f" last_development_changes : {dev}")
    return dev

def version_name(args=None):
    name = readconfig().get("version_name",{}) 
    logger.info(f"version_name : {name}")
    return name 
def is_stable(args=None):
    stable = readconfig().get("stable",{}) 
    logger.info(f"Is_stable : {stable}")
    return stable


def elysium_info(args=None):
    print(f""" 
    
    Version : {version()},
    Version Name  : {version_name()},
    Stable : {is_stable()}
    Last Development Changes : {last_development_changes()}

    """)

def check_version(args=None):
    el_updater = Updater()
    update = el_updater.check_update()
    logger.info(f"Update Status : {update}")
    return update

def update(args:None):
   el_updater = Updater()
   el_updater.update_elysium()

def ram_info(args:None):
    info:dict = dict(linux.show_ram_info())
    print(f"""
total: {int(info.get("total",""))}GB
used: {int(info.get("used",""))}GB
swap: {int(info.get("swap",""))}GB
free: {int(info.get("free",""))}GB
    """)

    return info
    
def cache_info(args:None):
    info = linux.show_cache_info()
    total:dict = dict(info.get("total_cache",{}))
    application_caches:dict = dict(info.get("application_cache",{}))
    print()
    for _,(application,cache) in enumerate(application_caches.items()):
       print(f"{application:^6}------{cache}") 
    print()

    print(f"Total:{total.get("used")}")

def remove_cache(args:None):
    if not linux.delete_cache():
        raise Exception ("Something went wrong")
    
