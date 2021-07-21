import pytest

from cloudconstruct.utils import config as utils
from cloudconstruct.utils.config import Config

TEST_CONFIG_DICT = {
    'key_1': 'value_1',
    'nested_key_1': {
        'key_2': 'value_2',
        'nested_key_2': {
            'key_3': 'value_3'
        }
    }
}

@pytest.fixture
def sample_config() -> Config:
    return Config(TEST_CONFIG_DICT)

def test_get_config_with_key_that_exists(sample_config: Config):
    expected = Config({
        'key_2': 'value_2',
        'nested_key_2': {
            'key_3': 'value_3'
        }
    })

    returned = sample_config.get_config('nested_key_1')
    print(returned._config)
    assert sample_config.get_config('nested_key_1') == expected