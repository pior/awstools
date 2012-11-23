import unittest
import datetime

import mock

from awstools import display


class TestDisplay(unittest.TestCase):

    def test_format_stack_summary(self):
        stack = mock.MagicMock(
            stack_name="stack_name",
            stack_id="stack_id",
            stack_status="stack_status",
            creation_time="creation_time")

        fmt = display.format_stack_summary(
            stack
            )

        self.assertIn('stack_name', fmt)
        self.assertIn('stack_id', fmt)
        self.assertIn('stack_status', fmt)
        self.assertIn('creation_time', fmt)

    def test_format_stack_summary_oneline(self):
        stack = mock.MagicMock(
            stack_name="stack_name",
            stack_status="stack_status",
            creation_time="creation_time")

        fmt = display.format_stack_summary(
            stack,
            oneline=True,
            )

        self.assertIn('stack_name', fmt)
        self.assertIn('stack_status', fmt)
        self.assertIn('creation_time', fmt)

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
