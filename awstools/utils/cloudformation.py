# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>


import boto


STACK_IGNORE_STATUS = ["DELETE_COMPLETE"]

def find_stacks(pattern=None, findall=False):
    """Return a list of stacks matching a pattern"""

    cfn = boto.connect_cloudformation()
    stacks = []
    next_token = None
    while True:
        result = cfn.list_stacks(next_token=next_token)
        stacks.extend(result)
        next_token = result.next_token
        if next_token is None:
            break

    if pattern:
        stacks = [s for s in stacks if pattern in s.stack_name]

    if not findall:
        stacks = [s for s in stacks
                  if s.stack_status not in STACK_IGNORE_STATUS]

    return sorted(stacks, key=lambda k: k.stack_name)


def find_one_stack(pattern, findall=False, summary=True):
    """Return the result is there is only one. Raise ValueError otherwise"""
    stacks = find_stacks(pattern=pattern, findall=findall)

    for stack in stacks:        # If we have an exact match, just take it
        if stack.stack_name == pattern:
            stacks = [stack]
            break

    if len(stacks) > 1:
        raise ValueError("More than one stack matched this pattern: %s" % (
                         pattern))
    if len(stacks) == 0:
        raise ValueError("No stack found with pattern: %s" % pattern)
    if summary:
        return stacks[0]
    else:
        cfn = boto.connect_cloudformation()
        return cfn.describe_stacks(stacks[0].stack_name)[0]


RES_TYPE_ASG = 'AWS::AutoScaling::AutoScalingGroup'
RES_TYPE_ELB = 'AWS::ElasticLoadBalancing::LoadBalancer'


def find_one_resource(stack, resource_type, only_id=False):
    stackresources = stack.describe_resources()

    resources = [r for r in stackresources if r.resource_type == resource_type]
    if len(resources) == 0:
        raise ValueError("This stack contains no AutoScale")
    if len(resources) > 1:
        raise ValueError("This stack contains more than one AutoScale")

    phy_id = resources[0].physical_resource_id

    if resource_type == RES_TYPE_ASG:
        if only_id:
            return phy_id
        else:
            try:
                return boto.connect_autoscale().get_all_groups([phy_id])[0]
            except IndexError:
                raise ValueError("The AutoScale physical id doesn't exist")

    elif resource_type == RES_TYPE_ELB:
        if only_id:
            return phy_id
        else:
            try:
                return boto.connect_elb().get_all_load_balancers([phy_id])[0]
            except IndexError:
                raise ValueError("The ELB physical id doesn't exist")

    else:
        raise NotImplementedError("Unkown resource type")
