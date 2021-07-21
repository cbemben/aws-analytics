import collections.abc
import copy
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import oyaml as yaml


log = logging.getLogger(__name__)


class Config:
    """ A Config object wraps a dictionary with additional
    functionality by supporting multi-level keys in a single call
    """
    def __init__(self, config_dict: dict):
        """ Initializes a `Config` that wraps the given dictionary
        """
        assert isinstance(config_dict, collections.abc.Mapping)

        self._config = config_dict

    def __getitem__(self, key) -> Any:
        return self._config[key]

    def __eq__(self, other: Union['Config', dict]) -> bool:
        if isinstance(other, Config):
            return self._config == other._config
        elif isinstance(other, collections.abc.Mapping):
            return self._config == other
        else:
            return False

    def get(self, *keys: str, default: Optional[Any] = None) -> Any:
        if not keys:
            raise ValueError("No keys specified")

        current = self._config
        for subkey in keys[:-1]:
            current = current.get(subkey, {})

            # If the returned value is not a dict but more keys
            # have been provided, return the default value
            if not isinstance(current, collections.abc.Mapping):
                return default

        return current.get(keys[-1], default)

    def get_config(self, *keys: str) -> 'Config':
        return Config(self.get(*keys, default={}))

def merge(old: Dict[Any, Any], new: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Merge the two dictionaries together into a single dictionary.
    Priority will go to the ``new`` dictionary object when the same
    key exists in both of the dictionaries.
    """
    for k, v in new.items():
        if isinstance(old, collections.abc.Mapping):
            if isinstance(v, collections.abc.Mapping):
                old[k] = merge(old.get(k, {}), v)
            else:
                old[k] = v
        else:
            old = {k: v}

    return old


def load_yaml(path: str) -> Dict[str, Any]:
    file_handle = open(path, 'r')
    res = yaml.safe_load(file_handle)
    file_handle.close()
    return res