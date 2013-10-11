# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import unittest
import StringIO

import argh

import mock


class TestCfnAs(unittest.TestCase):

    def setUp(self):
        self.stdout = StringIO.StringIO()
        self.stderr = StringIO.StringIO()

    def tearDown(self):
        self.assertEqual(
            0, self.stderr.len,
            msg="stderr is not empty:\n %s" % self.stderr.getvalue())

    @mock.patch('awstools.commands.cfnautoscale.boto.connect_cloudformation')
    @mock.patch('awstools.commands.cfnautoscale.find_stacks')
    @mock.patch('awstools.commands.cfnautoscale.format_autoscale_instances')
    def test_command_status(self, m_format, m_find_stacks, m_c_cfn):
        from awstools.commands import cfnautoscale

        m_format.side_effect = lambda x: "format: %s" % x

        stacks = [mock.Mock(stack_name='test_stack_name_1'),
                  mock.Mock(stack_name='test_stack_name_2'),
                  mock.Mock(stack_name='test_stack_name_3')]

        m_find_stacks.return_value = stacks
        m_c_cfn.return_value.describe_stacks.side_effect = zip(stacks)

        argh.dispatch_command(cfnautoscale.status,
                              argv=['testpattern'],
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        m_format.assert_has_called([mock.call(s) for s in stacks])

        for stack in stacks:
            self.assertIn(str(stack), self.stdout.getvalue())

    @mock.patch('awstools.commands.cfnautoscale.boto.connect_cloudformation')
    @mock.patch('awstools.commands.cfnautoscale.find_stacks')
    @mock.patch('awstools.commands.cfnautoscale.find_one_resource')
    def test_command_show_cfg(self, m_find_one_r, m_find_stacks, m_c_cfn):
        from awstools.commands import cfnautoscale
        from awstools.utils.cloudformation import RES_TYPE_ASG

        stacks = [mock.Mock(stack_name='test_stack_name_1'),
                  mock.Mock(stack_name='test_stack_name_2'),
                  mock.Mock(stack_name='test_stack_name_3')]

        resources = [mock.Mock(instances=[mock.Mock(launch_config_name='lc1')]),
                     mock.Mock(instances=[mock.Mock(launch_config_name='lc2')]),
                     mock.Mock(instances=[mock.Mock(launch_config_name='lc3')])]

        m_find_stacks.return_value = stacks
        m_c_cfn.return_value.describe_stacks.side_effect = zip(stacks)

        m_find_one_r.side_effect = resources

        argh.dispatch_command(cfnautoscale.show_cfg,
                              argv=['testpattern'],
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        for stack in stacks:
            self.assertIn(stack.stack_name, self.stdout.getvalue())

        for name in ['lc1', 'lc2', 'lc3']:
            self.assertIn(name, self.stdout.getvalue())

    @mock.patch('awstools.commands.cfnautoscale.find_one_stack')
    @mock.patch('awstools.commands.cfnautoscale.find_one_resource')
    @mock.patch('awstools.commands.cfnautoscale.format_autoscale')
    def test_command_metrics(self, m_format_as, m_find_one_r, m_find_one_s):
        from awstools.commands import cfnautoscale
        from awstools.utils.cloudformation import RES_TYPE_ASG

        stack = mock.Mock(stack_name='test_stack_name_1')

        resource = mock.Mock(enabled_metrics=['metric1', 'metric2'])

        m_find_one_s.return_value = stack
        m_find_one_r.return_value = resource

        argh.dispatch_command(cfnautoscale.metrics,
                              argv=['testpattern'],
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        m_find_one_s.assert_called_with('testpattern', summary=False)

        self.assertIn(stack.stack_name, self.stdout.getvalue())

        m_find_one_r.assert_called_with(stack, RES_TYPE_ASG)

        self.assertIn('metric1', self.stdout.getvalue())
        self.assertIn('metric2', self.stdout.getvalue())
