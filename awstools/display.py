# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import boto
import arrow
from prettytable import PrettyTable

from awstools.utils.cloudformation import (find_one_resource,
                                           RES_TYPE_ASG,
                                           RES_TYPE_ELB)


def humanize_date(d):
    return arrow.get(d).humanize()


def local_date(d):
    if d is None:
        return '-'
    return arrow.get(d).to('local').format('YYYY-MM-DD HH:mm:ss')


def long_date(d):
    return "%s (%s)" % (
        arrow.get(d).to('local').format('YYYY-MM-DD HH:mm:ss'),
        arrow.get(d).humanize(),
    )


def format_stack_summary(stack):
    tmpl = "Name: {s.stack_name}\n"
    tmpl += "Id: {s.stack_id}\n"
    tmpl += "Status: {s.stack_status} \n"
    tmpl += "Creation : {date}\n"

    if hasattr(stack, 'description'):
        tmpl += "Template: {s.description}"
    elif hasattr(stack, 'template_description'):
        tmpl += "Template: {s.template_description}"
    else:
        raise ValueError("Invalid Stack object")
    return tmpl.format(s=stack, date=long_date(stack.creation_time))


def format_stacks(stacks):
    tab = PrettyTable(['Name', 'Template', 'Status', 'Creation'])
    tab.align = 'l'

    for s in stacks:
        tab.add_row([
            s.stack_name,
            s.template_description,
            s.stack_status,
            local_date(s.creation_time),
        ])

    return tab.get_string()


def format_stack_events(stack, limit=None):
    if hasattr(stack, 'describe_events'):
        events = stack.describe_events()
    else:
        cfn = boto.connect_cloudformation()
        events = cfn.describe_stack_events(stack.stack_name)

    cfn = boto.connect_cloudformation()
    events = list(cfn.describe_stack_events(stack.stack_name))

    if limit is None:
        limit = len(events)

    tab = PrettyTable(['Time', 'Type', 'Logical ID', 'Status', 'Reason'])
    tab.align = 'l'

    for e in events:
        reason = e.resource_status_reason

        tab.add_row([local_date(e.timestamp),
                    e.resource_type,
                    e.logical_resource_id,
                    e.resource_status,
                    reason if reason is not None else ''])

    return tab.get_string(end=limit)


def format_stack_resources(stack):
    if hasattr(stack, 'describe_resources'):
        resources = stack.describe_resources()
    else:
        cfn = boto.connect_cloudformation()
        resources = cfn.describe_stack_resources(stack.stack_name)

    tab = PrettyTable(['Type', 'Status', 'Logical ID', 'Physical ID'])
    tab.align = 'l'
    tab.sortby = 'Type'

    for r in resources:
        if r.resource_type == 'AWS::CloudFormation::WaitConditionHandle':
            physical_resource_id = r.physical_resource_id[0:45] + '...'
        else:
            physical_resource_id = r.physical_resource_id

        tab.add_row([
            r.resource_type,
            r.resource_status,
            r.logical_resource_id,
            physical_resource_id])

    return tab.get_string()


def format_stack_outputs(stack):
    tab = PrettyTable(['Key', 'Value', 'Description'])
    tab.align = 'l'
    tab.sortby = 'Key'

    for o in stack.outputs:
        tab.add_row([o.key, o.value, o.description])

    return tab.get_string()


def format_stack_parameters(stack):
    tab = PrettyTable(['Key', 'Value'])
    tab.align = 'l'
    tab.sortby = 'Key'

    for p in stack.parameters:
        tab.add_row([p.key, p.value])

    return tab.get_string()


def format_autoscale(asg, detail=False):
    tmpl = ("AutoScaleGroup: {a.name}\n"
            "AutoScaleGroup min:{a.min_size} max:{a.max_size} "
            "capacity:{a.desired_capacity}\n")

    if detail:
        tmpl += "AutoScaleGroup instances:\n  {instances}"

    return tmpl.format(
        a=asg,
        instances='\n  '.join(map(repr, asg.instances)),
    )


def format_autoscale_instances(stack):
    s = []

    tmpl = "  ASG: {id} {health}/{state} LC:{lc}"

    res_asg = find_one_resource(stack, RES_TYPE_ASG)

    for i in res_asg.instances:
        s.append(tmpl.format(id=i.instance_id,
                             state=i.lifecycle_state,
                             health=i.health_status,
                             lc=i.launch_config_name))

    tmpl = "  ELB: {i.instance_id} {i.state} ({i.reason_code})"

    res_elb_id = find_one_resource(stack, RES_TYPE_ELB, only_id=True)
    ihealth = boto.connect_elb().describe_instance_health(res_elb_id)

    for i in ihealth:
        s.append(tmpl.format(i=i))

    return '\n'.join(s)
