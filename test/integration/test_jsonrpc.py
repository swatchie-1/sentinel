import pytest
import sys
import os
import re
os.environ['SENTINEL_ENV'] = 'test'
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../test_sentinel.conf'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import config

from hiluxd import HiluxDaemon
from hilux_config import HiluxConfig


def test_hiluxd():
    config_text = HiluxConfig.slurp_config_file(config.hilux_conf)
    network = 'mainnet'
    is_testnet = False
    genesis_hash = u'000008876cc4a4550d368ec40f7a1e8a17b665f422be9c53266b51ca3ab8b1d1'
    for line in config_text.split("\n"):
        if line.startswith('testnet=1'):
            network = 'testnet'
            is_testnet = True
            genesis_hash = u'00000bafbc94add76cb75e2ec92894837288a481e5c005f6563d91623bf8bc2c'

    creds = HiluxConfig.get_rpc_creds(config_text, network)
    hiluxd = HiluxDaemon(**creds)
    assert hiluxd.rpc_command is not None

    assert hasattr(hiluxd, 'rpc_connection')

    # Hilux testnet block 0 hash == 00000bafbc94add76cb75e2ec92894837288a481e5c005f6563d91623bf8bc2c
    # test commands without arguments
    info = hiluxd.rpc_command('getinfo')
    info_keys = [
        'blocks',
        'connections',
        'difficulty',
        'errors',
        'protocolversion',
        'proxy',
        'testnet',
        'timeoffset',
        'version',
    ]
    for key in info_keys:
        assert key in info
    assert info['testnet'] is is_testnet

    # test commands with args
    assert hiluxd.rpc_command('getblockhash', 0) == genesis_hash
