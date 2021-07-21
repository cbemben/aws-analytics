"""
The ``configuration`` module loads in the config specified by ``cloudconstruct/config.yml``
and optionally overwrites values specified in the user config ``cloudconstruct/config.usr.yml``
if it exists. The resultant config is stored as a module attribute and ``Config`` object that
is accessible via ::

    from cloudconstruct.config import conf
"""

from pathlib import Path, PurePath
from cloudconstruct.utils.config import Config, load_yaml, merge


DEFAULT_CONFIG = PurePath.joinpath(Path.cwd(), "cloudconstruct/config.yml")
USER_CONFIG = PurePath.joinpath(Path.cwd(), "cloudconstruct/config.usr.yml")


def _load_configuration(path: str, user_config_path: str = None) -> Config:
    """
    Loads in the cloudconstruct configuration

    :param str path: 
        The path to the YAML configuration file
    
    :param str user_config_path:
        Optional path to a user YAML configuration file. If it is provided, it will
        be used to overwrite the values from the configuration file provided in the first
        parameter.

    :return:
        cloudconstruct config
    """
    # Load default config
    default_config = load_yaml(path)

    # Load user config
    if user_config_path and Path.is_file(user_config_path):
        user_config = load_yaml(user_config_path)
        # Merge user config into default config
        default_config = merge(default_config, user_config)

    return Config(default_config)

# Load config
conf = _load_configuration(path=DEFAULT_CONFIG, user_config_path=USER_CONFIG)
