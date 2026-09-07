from elysium_config.path_config import check_for_eLysium_path
from errors.errors import ConfigFileMissing

if not check_for_eLysium_path():
    raise ConfigFileMissing ("there aint config file ")
