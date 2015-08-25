import os
from ConfigParser import ConfigParser


_DEFAULTS = {}


def read_config(alternate_config=None):
    """Helper for the configuration"""
    _config = ConfigParser(_DEFAULTS)
    if alternate_config:
        _config.read(os.path.expanduser(alternate_config))
    else:
        _config.read(['/etc/awstools.cfg',
                      os.path.expanduser('~/.awstools.cfg'),
                      'awstools.cfg'])
    return _config
