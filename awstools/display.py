# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@socialludia.com>

import boto


def format_stack_summary(stack, oneline=False):
    if oneline:
        return "{s.stack_name:<30} {s.stack_status:<30} {s.creation_time}".format(s=stack)
    else:
        return "\n".join(["Name: {}".format(stack.stack_name),
                          "Id: {}".format(stack.stack_id),
                          "Status: {}".format(stack.stack_status),
                          "Creation Time: {}".format(stack.creation_time)])


def format_stack_events(stack, limit=None):
    cfn = boto.connect_cloudformation()
    events = list(cfn.describe_stack_events(stack.stack_name))
    if limit:
        events = events[0:limit]

    def formatline(e):
        f = "{time}  {etype:<40}  {logicalid:<24}  {status:<20}  {reason}"
        return f.format(time=e.timestamp.isoformat().replace('T', ' '),
                        status=e.resource_status,
                        etype=e.resource_type,
                        logicalid=e.logical_resource_id,
                        reason=e.resource_status_reason)

    return "\n".join([formatline(e) for e in events])
