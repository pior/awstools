# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@socialludia.com>

import os

from argh import arg, alias, confirm, wrap_errors
from argh.exceptions import CommandError

import boto
from boto.exception import BotoServerError

from awstools.display import (format_stack_summary,
                              format_stack_summary_short,
                              format_stack_events)
from awstools.utils.cloudformation import (find_stacks,
                                           find_one_stack,
                                           find_one_resource)
from awstools.utils.autoscale import update_asg_capacity
from awstools.commands import initialize_from_cli, warn_for_live
from awstools import cfntemplate


HELP_SN = "the name of the stack like tt-python-production"
HELP_TMPL = "force a different template file"
HELP_CAP = "AutoScale desired capacity"
HELP_LIMITS = "Specify the MIN:MAX parameters (eg: 10:20 or :2)"


@arg('-a', '--all', default=False)
@arg('stack_name', nargs='?', default='')
@alias('list')
@wrap_errors([ValueError, BotoServerError])
def ls(args):
    stacks = find_stacks(args.stack_name, findall=args.all)
    for stack in stacks:
        yield format_stack_summary_short(stack)


@arg('stack_name', help=HELP_SN)
@arg('--template', help=HELP_TMPL)
@wrap_errors([ValueError, BotoServerError])
def create(args):
    config, settings, sinfo = initialize_from_cli(args)

    # Read template
    template_path = os.path.join(
        config.get("cfn", "templatedir"),
        args.template if args.template else sinfo['template'])
    template = cfntemplate.CfnTemplate(template_path)
    parameters = cfntemplate.CfnParameters(template, sinfo)

    print("\nStack name: {args.stack_name}\n"
          "\nTemplate: {template!r}\n"
          "\nParameters:\n"
          "{parameters!r}\n".format(args=args,
                                    template=template,
                                    parameters=parameters))

    if not confirm('Confirm this creation? ', default=True):
        raise CommandError("Aborted")

    try:
        stackid = boto.connect_cloudformation().create_stack(
            args.stack_name,
            template_body=template.body,
            parameters=parameters,
            capabilities=['CAPABILITY_IAM'])
        print("StackId %s" % stackid)
    except BotoServerError as e:
        if e.error_message:
            raise CommandError("BotoServerError: " + e.error_message)
        else:
            raise e


@arg('stack_name', help=HELP_SN)
@arg('--template', help=HELP_TMPL)
@wrap_errors([ValueError, BotoServerError])
def update(args):
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

    if not confirm('Confirm the update? ', default=True):
        raise CommandError("Aborted")

    try:
        stackid = boto.connect_cloudformation().update_stack(
            args.stack_name,
            template_body=template.body,
            parameters=parameters,
            capabilities=['CAPABILITY_IAM'])
        print("StackId %s" % stackid)
    except BotoServerError as e:
        if e.error_message:
            raise CommandError("BotoServerError: " + e.error_message)
        else:
            raise e


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def delete(args):
    config, settings, sinfo = initialize_from_cli(args)

    stack = find_one_stack(args.stack_name)

    print(format_stack_summary(stack))

    warn_for_live(sinfo)

    if not confirm('Confirm the deletion? ', default=True):
        raise CommandError("Aborted")

    try:
        res = boto.connect_cloudformation().delete_stack(stack.stack_name)
    except BotoServerError as e:
        if e:
            raise CommandError("BotoServerError: " + e.error_message)
        else:
            raise e
    print("Result %s" % res)


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def info(args):
    stack = find_one_stack(args.stack_name, summary=False)

    yield format_stack_summary(stack) + '\n'

    for param in stack.parameters:
        yield str(param)
    yield ''

    for output in stack.outputs:
        yield str(output)
    yield ''

    yield format_stack_events(stack, limit=10) + '\n'

    for resource in stack.describe_resources():
        yield "{r}\n  {r.resource_status} {r.physical_resource_id}".format(
            r=resource)
    yield ''


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def outputs(args):
    stack = find_one_stack(args.stack_name, summary=False)

    yield format_stack_summary(stack) + '\n'

    for output in stack.outputs:
        yield str(output)


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def resources(args):
    stack = find_one_stack(args.stack_name, summary=False)

    yield format_stack_summary(stack) + '\n'

    tmpl = "  ".join([
                     "{r.logical_resource_id:<24}",
                     "{r.physical_resource_id:<60}",
                     "[{r.resource_status}] {r.resource_type}"
                     ])

    for resource in stack.describe_resources():
        yield tmpl.format(r=resource)
    yield ''


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def events(args):
    stack = find_one_stack(args.stack_name, summary=False)
    yield format_stack_summary(stack) + '\n'
    yield format_stack_events(stack) + '\n'


def activities(args):
    stacks = find_stacks(None, findall=True)
    for stack in stacks:
        if stack.stack_status.endswith('_COMPLETE'):
            continue
        yield format_stack_summary_short(stack)


@arg('stack_name', help=HELP_SN)
@arg('limits', help=HELP_LIMITS)
@wrap_errors([ValueError, BotoServerError])
def setlimit(args):
    """
    Change the min and/or max parameters of the AutoScale in a stack
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    print(format_stack_summary(stack))

    warn_for_live(sinfo)

    asg = find_one_resource(stack, 'AWS::AutoScaling::AutoScalingGroup')
    print("AutoScale ID: %s" % asg.name)

    try:
        limits = args.limits.split(':')
        minlimit = int(limits[0]) if limits[0] else None
        maxlimit = int(limits[1]) if limits[1] else None
    except:
        raise ValueError("Invalid limit format ")

    update_asg_capacity(
        asg,
        minlimit=minlimit,
        maxlimit=maxlimit,
    )


@arg('stack_name', help=HELP_SN)
@arg('capacity', type=int, help=HELP_CAP)
@wrap_errors([ValueError, BotoServerError])
def setcapacity(args):
    """
    Change the "desired_capacity" parameter of the AutoScale in a stack
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    print(format_stack_summary(stack))

    warn_for_live(sinfo)

    asg = find_one_resource(stack, 'AWS::AutoScaling::AutoScalingGroup')
    print("AutoScale ID: %s" % asg.name)

    update_asg_capacity(
        asg,
        desired=args.capacity,
    )


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def shutdown(args):
    """
    Shutdown the stack: force the AutoScale to shut all instances down
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    print(format_stack_summary(stack))

    warn_for_live(sinfo)

    asg = find_one_resource(stack, 'AWS::AutoScaling::AutoScalingGroup')
    print("AutoScale ID: %s" % asg.name)

    update_asg_capacity(
        asg,
        desired=0,
        minlimit=0,
        maxlimit=0,
    )


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def startup(args):
    """
    Startup the stack: set AutoScale to start the instances up
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    print(format_stack_summary(stack))

    warn_for_live(sinfo)

    asg = find_one_resource(stack, 'AWS::AutoScaling::AutoScalingGroup')
    print("AutoScale ID: %s" % asg.name)

    try:
        minlimit = int(sinfo['AutoScaleMinSize'])
        maxlimit = int(sinfo['AutoScaleMaxSize'])
        desired = int(sinfo['AutoScaleDesiredCapacity'])
    except:
        raise ValueError("Invalid AutoScale information in stack definition")

    update_asg_capacity(
        asg,
        desired=desired,
        minlimit=minlimit,
        maxlimit=maxlimit,
    )
