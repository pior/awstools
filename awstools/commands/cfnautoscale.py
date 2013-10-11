# -*- coding: utf-8 -*-
# Copyright (C) 2013 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

from time import sleep

from argh import arg, confirm, wrap_errors
from argh.exceptions import CommandError

import boto
from boto.exception import BotoServerError

from awstools.display import (format_stack_summary,
                              format_autoscale,
                              format_autoscale_instances)
from awstools.utils.cloudformation import (find_stacks,
                                           find_one_stack,
                                           find_one_resource,
                                           RES_TYPE_ASG,
                                           RES_TYPE_ELB)
from awstools.commands import (get_base_parser,
                               initialize_from_cli,
                               warn_for_live,
                               confirm_action)

HELP_SN = "the name of the stack like tt-python-production"
HELP_TMPL = "force a different template file"
HELP_CAP = "AutoScale desired capacity"
HELP_MIN = "AutoScaleGroup min constraint"
HELP_MAX = "AutoScaleGroup max constraint"
HELP_DESIRED = "AutoScaleGroup desired value"
HELP_FORCE = "Don't ask for confirmation"


def main():
    parser = get_base_parser()

    parser.add_commands([status,
                         control,
                         stop,
                         start,
                         migrate_cfg,
                         show_cfg,
                         metrics])

    parser.dispatch(completion=False)


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def status(args):
    """
    List the status of the instances and ELB
    """

    stacks = find_stacks(args.stack_name)

    cfn = boto.connect_cloudformation()

    for stack in stacks:
        fullstack = cfn.describe_stacks(stack.stack_name)[0]
        yield "\nStack %s" % fullstack.stack_name
        yield format_autoscale_instances(fullstack)


@arg('stack_name', help=HELP_SN)
@arg('min', nargs='?', help=HELP_MIN)
@arg('max', nargs='?', help=HELP_MAX)
@arg('desired', nargs='?', help=HELP_DESIRED)
@arg('-f', '--force', default=False, help=HELP_FORCE)
@wrap_errors([ValueError, BotoServerError])
def control(args):
    """
    Control the stack: update the AutoScaleGroup constraints
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    yield format_stack_summary(stack) + '\n'

    asg = find_one_resource(stack, RES_TYPE_ASG)
    yield format_autoscale(asg)

    if args.min or args.max or args.desired:
        try:
            asg.min_size = int(args.min)
            asg.max_size = int(args.max)
            asg.desired_capacity = int(args.desired)
        except ValueError as error:
            raise CommandError("Invalid value for ASG: %s" % error)

        yield "Change to:"
        yield format_autoscale(asg)

        warn_for_live(sinfo)
        confirm_action(arg, default=True)

        asg.update()
        yield "Updated"


@arg('stack_name', help=HELP_SN)
@arg('-f', '--force', default=False, help=HELP_FORCE)
@wrap_errors([ValueError, BotoServerError])
def stop(args):
    """
    Stop the stack: force the AutoScale to shut all instances down
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    yield format_stack_summary(stack)

    asg = find_one_resource(stack, RES_TYPE_ASG)
    yield format_autoscale(asg)

    asg.min_size = 0
    asg.max_size = 0
    asg.desired_capacity = 0

    yield "Change to:"
    yield format_autoscale(asg)

    warn_for_live(sinfo)
    confirm_action(arg, default=True)

    asg.update()
    yield "Updated"


@arg('stack_name', help=HELP_SN)
@arg('-f', '--force', default=False, help=HELP_FORCE)
@wrap_errors([ValueError, BotoServerError])
def start(args):
    """
    Start the stack: set AutoScale control to configured values
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    print(format_stack_summary(stack))

    asg = find_one_resource(stack, RES_TYPE_ASG)
    yield format_autoscale(asg)

    try:
        asg.min_size = int(sinfo['AutoScaleMinSize'])
        asg.max_size = int(sinfo['AutoScaleMaxSize'])
        asg.desired_capacity = int(sinfo['AutoScaleDesiredCapacity'])
    except ValueError as error:
        raise CommandError("Invalid values in stack definition: %s" % error)

    yield "Change to:"
    yield format_autoscale(asg)

    warn_for_live(sinfo)
    confirm_action(arg, default=True)

    asg.update()
    yield "Updated"


@arg('stack_name', help=HELP_SN)
@wrap_errors([ValueError, BotoServerError])
def show_cfg(args):
    """
    List the instance with AutoScale launch config
    """
    stacks = find_stacks(args.stack_name)

    cfn = boto.connect_cloudformation()

    for stack in stacks:
        yield "Stack %s" % stack.stack_name

        stack = cfn.describe_stacks(stack.stack_name)[0]

        asg = find_one_resource(stack, RES_TYPE_ASG)
        for instance in asg.instances:
            yield "  {i!r} LC:{i.launch_config_name}".format(i=instance)


@arg('stack_name', help=HELP_SN)
@arg('-f', '--force', default=False, help=HELP_FORCE)
@wrap_errors([ValueError, BotoServerError])
def migrate_cfg(args):
    """
    Migrate the stack: re-instantiate all instances
    """
    config, settings, sinfo = initialize_from_cli(args)
    stack = find_one_stack(args.stack_name, summary=False)
    print(format_stack_summary(stack))

    asg = find_one_resource(stack, RES_TYPE_ASG)
    yield format_autoscale(asg)

    orig_min = asg.min_size
    orig_max = asg.max_size
    orig_desired = asg.desired_capacity
    orig_term_pol = asg.termination_policies
    orig_instances = asg.instances

    mig_min = orig_desired * 2
    mig_max = orig_desired * 2
    mig_desired = orig_desired * 2
    mig_term_pol = [u'OldestLaunchConfiguration', u'OldestInstance']

    if orig_desired != len(asg.instances):
        raise CommandError("The ASG is not stable (desired != instances)")

    for instance in asg.instances:
        if instance.health_status != 'Healthy':
            raise CommandError("The ASG is not stable (instance not healthy)")

    warn_for_live(sinfo)
    confirm_action(arg, default=True)

    yield "\n <> Setting termination policy to %s" % mig_term_pol
    asg.termination_policies = mig_term_pol
    asg.update()

    yield "\n <> Growing the desired capacity from %s to %s" % (
        orig_desired, mig_desired)
    asg.min_size = mig_min
    asg.max_size = mig_max
    asg.desired_capacity = mig_desired
    asg.update()

    yield "\n <> Waiting instances to stabilize..."
    while True:
        sleep(30)
        asg = find_one_resource(stack, RES_TYPE_ASG)
        res_elb_id = find_one_resource(stack, RES_TYPE_ELB, only_id=True)
        elbinstances = boto.connect_elb().describe_instance_health(res_elb_id)
        if len(asg.instances) < mig_desired:
            yield "    NOTYET: only %i instances created" % len(asg.instances)
            continue
        elif [i for i in asg.instances if i.health_status != 'Healthy']:
            yield "    NOTYET: still unhealthy instances"
            continue
        elif len(elbinstances) < mig_desired:
            yield "    NOTYET: only %i instances in ELB" % len(elbinstances)
            continue
        elif [i for i in elbinstances if i.state != 'InService']:
            yield "    NOTYET: not all instances are ELB:InService"
            continue
        else:
            yield "    OK: %s healthy instances in ELB" % len(asg.instances)
            break

    yield "\n <> Checking new ASG state..."
    asg = find_one_resource(stack, RES_TYPE_ASG)
    yield format_autoscale(asg)
    yield format_autoscale_instances(stack)

    yield "\n <> Restoring previous ASG control:"
    asg.termination_policies = orig_term_pol
    asg.min_size = orig_min
    asg.max_size = orig_max
    asg.desired_capacity = orig_desired
    yield format_autoscale(asg)

    if confirm('Restoring ASG config?', default=True):
        try:
            asg.update()
        except BotoServerError as error:
            yield "\n <> Restoration failed!"
            yield error
        else:
            yield "\n <> ASG control restored."
    else:
        yield "WARNING: The ASG desired capacity was doubled!"


@arg('stack_name', help=HELP_SN)
@arg('--enable', default=False)
@arg('--disable', default=False)
@wrap_errors([ValueError, BotoServerError])
def metrics(args):
    """
    Control the metrics collection activation
    """
    stack = find_one_stack(args.stack_name, summary=False)
    yield format_stack_summary(stack) + '\n'

    asg = find_one_resource(stack, RES_TYPE_ASG)
    yield format_autoscale(asg)

    if args.enable and args.disable:
        raise CommandError("Option --enable and --disable are not compatible")
    elif args.enable:
        asg.connection.enable_metrics_collection(asg.name,
            granularity='1Minute')
        yield "Updated"
    elif args.disable:
        asg.connection.disable_metrics_collection(asg.name)
        yield "Updated"
    else:
        yield "Metrics collection:"
        for metric in asg.enabled_metrics:
            yield "    %s" % metric
