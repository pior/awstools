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
                              format_stack_events,
                              format_autoscale)
from awstools.utils.cloudformation import (find_stacks,
                                           find_one_stack,
                                           find_one_resource)
from awstools.utils.autoscale import update_asg
from awstools.commands import initialize_from_cli, warn_for_live
from awstools import cfntemplate


HELP_SN = "the name of the stack like tt-python-production"
HELP_TMPL = "force a different template file"
HELP_CAP = "AutoScale desired capacity"
HELP_MIN = "AutoScaleGroup min constraint"
HELP_MAX = "AutoScaleGroup max constraint"
HELP_DESIRED = "AutoScaleGroup desired value"
HELP_FORCE = "Don't ask for confirmation"


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
@arg('-f', '--force', default=False, help=HELP_FORCE)
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

    if not args.force:
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


@arg('stack_name', nargs='?', default='')
@arg('-f', '--force', default=False, help=HELP_FORCE)
@wrap_errors([ValueError, BotoServerError])
def batch_update(args):
    args.template = None

    stacks = find_stacks(args.stack_name)
    for stack in stacks:
        yield format_stack_summary_short(stack)

    if not confirm('Confirm the batch update? ', default=False):
        raise CommandError("Aborted")

    for stack in stacks:
        args.stack_name = stack.stack_name
        try:
            update(args)
        except CommandError as error:
            print error
            if not confirm('Continue anyway?', default=True):
                raise


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
@arg('min', nargs='?', help=HELP_MIN)
@arg('max', nargs='?', help=HELP_MAX)
@arg('desired', nargs='?', help=HELP_DESIRED)
@wrap_errors([ValueError, BotoServerError])
def as_control(args):
    """
    Control the stack: update the AutoScaleGroup constraints
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    yield format_stack_summary(stack) + '\n'

    asg = find_one_resource(stack, 'AWS::AutoScaling::AutoScalingGroup')
    yield format_autoscale(asg)

    if args.min or args.max or args.desired:
        try:
            minlimit = int(args.min)
            maxlimit = int(args.max)
            desired = int(args.desired)
        except:
            raise ValueError("Invalid value")

        warn_for_live(sinfo)

        updated = update_asg(
            asg,
            minlimit=minlimit,
            maxlimit=maxlimit,
            desired=desired,
        )

        if updated:
            yield "Updated: %s" % ' '.join(updated)
            yield format_autoscale(asg)
        else:
            yield "Nothing changed"


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def as_stop(args):
    """
    Stop the stack: force the AutoScale to shut all instances down
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    yield format_stack_summary(stack)

    asg = find_one_resource(stack, 'AWS::AutoScaling::AutoScalingGroup')
    yield format_autoscale(asg)

    warn_for_live(sinfo)

    updated = update_asg(
        asg,
        minlimit=0,
        maxlimit=0,
        desired=0,
    )

    if updated:
        yield "Updated: %s" % ' '.join(updated)
        yield format_autoscale(asg)
    else:
        yield "Nothing changed"


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def as_start(args):
    """
    Start the stack: set AutoScale control to configured values
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    print(format_stack_summary(stack))

    asg = find_one_resource(stack, 'AWS::AutoScaling::AutoScalingGroup')
    yield format_autoscale(asg)

    try:
        minlimit = int(sinfo['AutoScaleMinSize'])
        maxlimit = int(sinfo['AutoScaleMaxSize'])
        desired = int(sinfo['AutoScaleDesiredCapacity'])
    except:
        raise ValueError("Invalid AutoScale information in stack definition")

    warn_for_live(sinfo)

    updated = update_asg(
        asg,
        minlimit=minlimit,
        maxlimit=maxlimit,
        desired=desired,
    )

    if updated:
        yield "Updated: %s" % ' '.join(updated)
        yield format_autoscale(asg)
    else:
        yield "Nothing changed"
