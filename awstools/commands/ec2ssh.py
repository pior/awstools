# -*- coding: utf-8 -*-
# Copyright (C) 2013 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import os
import json
import subprocess

import argh
from argh.exceptions import CommandError

from awstools.utils import ec2

HELP_INSTANCE = "Instance or list of instances"
HELP_COMMAND = "Command to run on the instances"
HELP_LIST = "List instances by name"
HELP_CONFIRM = "Always confirm"
HELP_VERBOSE = "Verbose mode"
HELP_ONE = "Run on the first instance found only"
HELP_YES = "Always answer yes"
HELP_COMPLETION = "Helper for completion (list eventually uptodate)"
HELP_COMPLETION = "Output a script to setup bash completion"



@argh.arg('instance', default=None, nargs='?', help=HELP_INSTANCE)
@argh.arg('command', default=None, nargs='*', help=HELP_COMMAND)
@argh.arg('-l', '--list', default=False, help=HELP_LIST)
@argh.arg('-c', '--confirm', default=False, help=HELP_CONFIRM)
@argh.arg('-v', '--verbose', default=False, help=HELP_VERBOSE)
@argh.arg('-y', '--yes', default=False, help=HELP_YES)
@argh.arg('-1', '--one', default=False, help=HELP_ONE)
@argh.arg('--completion-list', default=False)
@argh.arg('--completion-script', default=False, help=HELP_COMPLETION)
def connect(args):
    """SSH to multiple EC2 instances by name, instance-id or private ip"""

    if args.completion_list:
        try:
            yield " ".join(read_completion_list())
        except IOError:
            pass

    elif args.completion_script:
        yield BASH_COMPLETION_INSTALL_SCRIPT

    elif args.list:
        instances = ec2.get_instances()
        names = sorted([ec2.get_name(i) for i in instances])
        yield '\n'.join(names)

    elif args.instance is None:
        raise CommandError("No instances specified.")

    else:
        if args.confirm and args.yes:
            raise CommandError("Option confirm and yes are not compatible")

        try:
            instances = ec2.get_instances()
            write_completion_list(instances)

            specifiers = args.instance.lower().strip().split(',')
            instances = ec2.filter_instances(specifiers, instances)
            if len(instances) == 0:
                raise CommandError("No instances found.")
        except KeyboardInterrupt:
            raise CommandError("Killed while accessing AWS api.")

        if args.one:
            instances = instances[0:1]

        if len(instances) > 1 or args.confirm:
            args.verbose = True
        if len(instances) > 1 and not args.yes:
            args.confirm = True

        if args.verbose and args.command:
            yield '----- Command: %s' % ' '.join(args.command)
        if args.verbose:
            names = sorted([ec2.get_name(i) for i in instances])
            yield '----- Instances(%s): %s' % (len(names), ",".join(names))

        if args.confirm:
            if not argh.confirm('Connect to all instances (y) or just one (n)',
                                default=True):
                instances = [instances[0]]

        if len(instances) == 1:
            host = instances[0].public_dns_name
            try:
                os.execvp('ssh', ['ec2ssh', host] + args.command)
            except OSError as error:
                raise Exception("Failed to call the ssh command: %s" % error)
        else:
            for instance in instances:
                if args.verbose:
                    yield "----- %s: %s  %s" % (
                        instance.id,
                        instance.public_dns_name,
                        instance.private_ip_address,
                        )

                host = instance.public_dns_name
                subprocess.call(['ssh', host] + args.command)

        if args.verbose:
            yield '----- DONE'


def write_completion_list(instances):
    names = sorted([ec2.get_name(i) for i in instances])
    fname = os.path.expanduser("~/.ec2ssh_completion")
    with open(fname, 'wb') as fp:
        json.dump(names, fp, indent=2)


def read_completion_list():
    fname = os.path.expanduser("~/.ec2ssh_completion")
    with open(fname, 'rb') as fp:
        return json.load(fp)


BASH_COMPLETION_INSTALL_SCRIPT = """
_ec2ssh()
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    case $cur in
        -*)
            case $prev in
                *)
                    opts="-l --list -c --confirm -v --verbose -y --yes -1 --one --completion-list --completion-script"
                ;;
            esac
            ;;
        *)
            opts="$(ec2ssh --completion-list)"
                ;;
    esac
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _ec2ssh ec2ssh
"""
