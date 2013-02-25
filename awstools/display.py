# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@socialludia.com>

import boto


def format_stack_summary(stack):
    tmpl = "Name: {s.stack_name}\n"
    tmpl += "Id: {s.stack_id}\n"
    tmpl += "Status: {s.stack_status}\n"
    tmpl += "Creation : {s.creation_time}\n"

    if hasattr(stack, 'description'):
        tmpl += "Template: {s.description}"
    elif hasattr(stack, 'template_description'):
        tmpl += "Template: {s.template_description}"
    else:
        raise ValueError("Invalid Stack object")
    return tmpl.format(s=stack)


def format_stack_summary_short(stack):
    tmpl = u"{s.stack_name:<26} {s.stack_status:<18} {s.creation_time}"

    if hasattr(stack, 'description'):
        tmpl += u" - {s.description}"
    elif hasattr(stack, 'template_description'):
        tmpl += u" - {s.template_description}"
    else:
        raise ValueError("Invalid Stack object")
    return tmpl.format(s=stack)


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
