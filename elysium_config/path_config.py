"""
This file contains Path config stuff some functions are :
to download config / to check for path / to get path 
"""


import json
import os
from pathlib import Path

import requests

from logger_config import set_up_logger

BASEDIR = Path(__file__).parent
GENERAL_CONFIG_PATH = f"{BASEDIR}/path_config.json"
logger = set_up_logger(name="ElysiumConfig.path_config")

def get_elysium_path(of:str=""):
    with open(GENERAL_CONFIG_PATH,"r") as data:        
        config = json.load(data)
    elysium_path = config.get("elysium_paths",{})
    return elysium_path.get(of)


ELYSIUM_PATH= f"{Path.home()}/{get_elysium_path(of="Root_path")}"


def check_for_eLysium_path(path:str="")-> bool:
    elysium_path = path
    if not path:
        elysium_path = ELYSIUM_PATH    
    try:
        if os.path.exists(elysium_path):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def show_elysium_paths(all:bool=False)->dict:
    paths = {}
    with open(GENERAL_CONFIG_PATH,"r") as file:
        data = json.load(file)
    elysium_paths = data
    if not all:
        for i ,path_name in enumerate(elysium_paths,start=1):
         paths[i] = path_name
        return paths
    return data

def download_config(dir:str,url:str,download:bool=True):
    if dir=="" or url=="":
        raise Exception ("dir or url is not provided !")
    file_name = Path(url).name
    path = f"{dir}/{file_name}"
    is_json = file_name.endswith(".json")
    logger.info(path)
    try:
        response = requests.get(url)
        response.raise_for_status()
        if not download:
            return response.json() if is_json else response.text
        with open(path,'w')as data:
            if is_json:
                json.dump(response.json(),data,indent=2)
            else:
                data.write(response.text)
        return True
    except requests.ConnectTimeout:
        raise Exception ("timed out")
    except requests.HTTPError:
        raise Exception("http error")
    except requests.ReadTimeout:
        raise Exception("is server dead ")
    except Exception as e:
        print(f"Some thing went wrong ! {e}")
    return False 

def read_json(path:str) -> dict: #type:ignore
    """  
    This function willr read json ONLY ! 

    ARGS:
     path:str= "/home/user/pathtoajson"

    """
    try:
        logger.info(f"Reading JSON {path}")
        with open(path,'r') as file:
            data = json.load(file)
        return data
    except  Exception as e:
        logger.error(e)
        return {"e":e} 
