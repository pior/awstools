# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import unittest
import datetime

import mock
import boto.cloudformation.stack

from awstools import display


class TestDisplay(unittest.TestCase):

    def test_format_stack_summary(self):
        stack = boto.cloudformation.stack.StackSummary()
        stack.stack_name = "stack_name"
        stack.stack_status = "stack_status"
        stack.creation_time = "creation_time"
        stack.template_description = "template_description"

        stacksummary = boto.cloudformation.stack.Stack()
        stacksummary.stack_name = "stack_name"
        stacksummary.stack_status = "stack_status"
        stacksummary.creation_time = "creation_time"
        stacksummary.description = "template_description"

        fmt = display.format_stack_summary(stack)
        self.assertIn('stack_name', fmt)
        self.assertIn('stack_status', fmt)
        self.assertIn('creation_time', fmt)
        self.assertIn('template_description', fmt)

        fmt = display.format_stack_summary_short(stack)
        self.assertIn('stack_name', fmt)
        self.assertIn('stack_status', fmt)
        self.assertIn('creation_time', fmt)
        self.assertIn('template_description', fmt)

        fmt = display.format_stack_summary(stacksummary)
        self.assertIn('stack_name', fmt)
        self.assertIn('stack_status', fmt)
        self.assertIn('creation_time', fmt)
        self.assertIn('template_description', fmt)

        fmt = display.format_stack_summary_short(stacksummary)
        self.assertIn('stack_name', fmt)
        self.assertIn('stack_status', fmt)
        self.assertIn('creation_time', fmt)
        self.assertIn('template_description', fmt)

    @mock.patch('boto.connect_cloudformation')
    def test_format_stack_events(self, mock_cfn):
        stack = mock.MagicMock(stack_name="stack_name")

        event = mock.Mock(
            timestamp=datetime.datetime.min,
            resource_status='resource_status',
            resource_type='resource_type',
            logical_resource_id='logical_resource_id',
            resource_status_reason='resource_status_reason')

        mock_cfn.return_value = mock.MagicMock(
            describe_stack_events=lambda x: [event]
        )

        fmt = display.format_stack_events(stack)

        self.assertIn(event.resource_status, fmt)
        self.assertIn(event.resource_type, fmt)
        self.assertIn(event.logical_resource_id, fmt)
        self.assertIn(event.resource_status_reason, fmt)
