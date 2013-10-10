# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import os
import pkg_resources

from argh import (ArghParser, confirm)
from argh.exceptions import CommandError

import awstools
from awstools.application import Applications


def get_base_parser():
    dist = pkg_resources.get_distribution("awstools")
    parser = ArghParser(version=dist.version)
    parser.add_argument('--config', default=None,
        help="path of an alternative configuration file")
    parser.add_argument('--settings', default=None,
        help="path of the application settings configuration file")

    return parser


def initialize_from_cli(args):
    """
    Read the configuration and settings file and lookup for a stack_info"""

    config = awstools.read_config(args.config)

    if args.settings:
        settings = args.settings
    else:
        settings = config.get("cfn", "settings")

    settings_data = open(os.path.expanduser(settings), 'rb')

    if hasattr(args, 'stack_name'):
        apps = Applications(settings_data)
        app = apps.get(stackname=args.stack_name)
        sinfo = app.get_stack_info_from_stackname(args.stack_name)
    else:
        sinfo = None

    return config, settings, sinfo


def warn_for_live(sinfo):
    if sinfo['live'] and sinfo['Environment'] == 'production':
        if not confirm("WARNING: Updating a live stack! Are you sure? "):
            raise CommandError("Aborted")


def confirm_action(arg, action="action", default=False):
    if hasattr(arg, 'force') and arg.force:
        return

    if not confirm('Confirm %s? ' % action, default=default):
        raise CommandError("Aborted")
