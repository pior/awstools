# -*- coding: utf-8 -*-
# Copyright (C) 2013 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import os

from argh import arg, alias, confirm, wrap_errors
from argh.exceptions import CommandError

import boto
from boto.exception import BotoServerError

from awstools.display import (format_stack_summary, format_stack_outputs,
                              format_stacks, format_stack_resources,
                              format_stack_parameters,
                              format_stack_events)
from awstools.utils.cloudformation import (find_stacks,
                                           find_one_stack)
from awstools.commands import (get_base_parser,
                               initialize_from_cli,
                               warn_for_live,
                               confirm_action)
from awstools import cfntemplate


HELP_SN = "the name of the stack like tt-python-production"
HELP_TMPL = "force a different template file"
HELP_CAP = "AutoScale desired capacity"
HELP_MIN = "AutoScaleGroup min constraint"
HELP_MAX = "AutoScaleGroup max constraint"
HELP_DESIRED = "AutoScaleGroup desired value"
HELP_FORCE = "Don't ask for confirmation"
HELP_FULL_LIST = "Display the full list"


def main():
    parser = get_base_parser()

    parser.add_commands([ls,
                         create,
                         update,
                         batch_update,
                         delete,
                         info,
                         outputs,
                         parameters,
                         resources,
                         events,
                         activities,])

    parser.dispatch(completion=False)


@arg('-a', '--all', default=False)
@arg('stack_name', nargs='?', default='')
@alias('list')
@wrap_errors([ValueError, BotoServerError])
def ls(args):
    """
    list stacks
    """
    stacks = find_stacks(args.stack_name, findall=args.all)
    yield format_stacks(stacks)


@arg('stack_name', help=HELP_SN)
@arg('--template', help=HELP_TMPL)
@wrap_errors([ValueError, BotoServerError])
def create(args):
    """
    create a stack
    """
    config, settings, sinfo = initialize_from_cli(args)

    # Read template
    template_path = os.path.join(
        config.get("cfn", "templatedir"),
        args.template if args.template else sinfo['template'])
    template = cfntemplate.CfnTemplate(template_path)
    parameters = cfntemplate.CfnParameters(template, sinfo)
    tags = {
        'Name': args.stack_name,
        'Application': sinfo['Application'],
        'Environment': sinfo['Environment'],
        'Type': sinfo['Type'],
    }

    print("\nStack name: {args.stack_name}\n"
          "\nTemplate: {template!r}\n"
          "\nTags: {tags!r}\n"
          "\nParameters:\n{parameters!r}\n".format(args=args,
                                                   template=template,
                                                   parameters=parameters,
                                                   tags=tags))

    confirm_action(arg, default=True)

    try:
        stackid = boto.connect_cloudformation().create_stack(
            args.stack_name,
            template_body=template.body,
            parameters=parameters,
            tags=tags,
            capabilities=['CAPABILITY_IAM'])
        print("StackId %s" % stackid)
    except BotoServerError as error:
        if error.error_message:
            raise CommandError("BotoServerError: " + error.error_message)
        else:
            raise error


@arg('stack_name', help=HELP_SN)
@arg('--template', help=HELP_TMPL)
@arg('-f', '--force', default=False, help=HELP_FORCE)
@wrap_errors([ValueError, BotoServerError])
def update(args):
    """
    update a stack
    """
    config, settings, sinfo = initialize_from_cli(args)

    # Read template
    template = cfntemplate.CfnTemplate(
        os.path.join(
            config.get("cfn", "templatedir"),
            args.template if args.template else sinfo['template']
        )
    )

    parameters = cfntemplate.CfnParameters(template, sinfo)

    print("\nStack name: {args.stack_name}\n"
          "\nTemplate: {template!r}\n"
          "\nParameters:\n"
          "{parameters!r}\n".format(args=args,
                                    template=template,
                                    parameters=parameters))

    warn_for_live(sinfo)
    confirm_action(arg, default=True)

    try:
        stackid = boto.connect_cloudformation().update_stack(
            args.stack_name,
            template_body=template.body,
            parameters=parameters,
            capabilities=['CAPABILITY_IAM'])
        print("StackId %s" % stackid)
    except BotoServerError as error:
        if error.error_message:
            raise CommandError("BotoServerError: " + error.error_message)
        else:
            raise error


@arg('stack_name', nargs='?', default='')
@arg('-f', '--force', default=False, help=HELP_FORCE)
@wrap_errors([ValueError, BotoServerError])
def batch_update(args):
    """
    update a batch of stacks sequentially
    """
    args.template = None

    stacks = find_stacks(args.stack_name)
    yield format_stacks(stacks)

    confirm_action(arg, default=False)

    for stack in stacks:
        args.stack_name = stack.stack_name
        try:
            update(args)
        except CommandError as error:
            print error
            if not confirm('Continue anyway?', default=True):
                raise


@arg('stack_name', help=HELP_SN)
@arg('-f', '--force', default=False, help=HELP_FORCE)
@wrap_errors([ValueError, BotoServerError])
def delete(args):
    """
    delete a stack
    """
    config, settings, sinfo = initialize_from_cli(args)

    stack = find_one_stack(args.stack_name)
    yield format_stack_summary(stack)

    warn_for_live(sinfo)
    confirm_action(arg, default=True)

    try:
        res = boto.connect_cloudformation().delete_stack(stack.stack_name)
    except BotoServerError as error:
        if error:
            raise CommandError("BotoServerError: " + error.error_message)
        else:
            raise error
    print("Result %s" % res)


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def info(args):
    """
    display information of a stack
    """
    stack = find_one_stack(args.stack_name, summary=False)

    yield format_stack_summary(stack)
    yield ''

    yield format_stack_parameters(stack)
    yield ''

    yield format_stack_outputs(stack)
    yield ''

    yield format_stack_events(stack, limit=10)
    yield ''

    yield format_stack_resources(stack)
    yield '\n'


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def outputs(args):
    """
    display outputs of a stack
    """
    stack = find_one_stack(args.stack_name, summary=False)

    yield format_stack_summary(stack)
    yield ''

    yield format_stack_outputs(stack)


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def parameters(args):
    """
    display parameters of a stack
    """
    stack = find_one_stack(args.stack_name, summary=False)

    yield format_stack_summary(stack)
    yield ''

    yield format_stack_parameters(stack)


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def resources(args):
    """
    display resources of a stack
    """
    stack = find_one_stack(args.stack_name, summary=False)

    yield format_stack_summary(stack)
    yield ''

    yield format_stack_resources(stack)
    yield ''



@arg('stack_name', help=HELP_SN)
@arg('-a', '--all', default=False, help=HELP_FULL_LIST)
@wrap_errors([ValueError, BotoServerError])
def events(args):
    """
    display events of a stack
    """
    stack = find_one_stack(args.stack_name, summary=False)
    yield format_stack_summary(stack) + '\n'
    if args.all:
        yield format_stack_events(stack)
    else:
        yield format_stack_events(stack, limit=20)
    yield ''


def activities(args):
    """
    display global activity
    """
    stacks = find_stacks(None, findall=True)
    stacks = [s for s in stacks if not s.stack_status.endswith('_COMPLETE')]
    yield format_stacks(stacks)
    yield ''
