# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

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
