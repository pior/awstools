# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import time
import unittest
import StringIO

import argh
import boto


class TestCfn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfn = boto.connect_cloudformation()
        stacks = []
        next_token = None
        while True:
            result = cls.cfn.list_stacks(next_token=next_token)
            stacks.extend(result)
            next_token = result.next_token
            if next_token is None:
                break

        cls.stacks = [s for s in stacks if s.stack_status != 'DELETE_COMPLETE']

        # TODO: mock boto to avoid hitting (and being throttled by) AWS
        time.sleep(5)


    def setUp(self):
        self.stdout = StringIO.StringIO()
        self.stderr = StringIO.StringIO()

    def tearDown(self):
        self.assertEqual(
            0, self.stderr.len,
            msg="stderr is not empty:\n %s" % self.stderr.getvalue())

        time.sleep(2)  # Protection against AWS api throttling

    def test_command_ls(self):
        from awstools.commands import cloudformation

        argh.dispatch_command(cloudformation.ls,
                              argv=[],
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        for stack in self.stacks:
            self.assertIn(stack.stack_name, self.stdout.getvalue())

    def test_command_outputs(self):
        from awstools.commands import cloudformation

        argh.dispatch_command(cloudformation.outputs,
                              argv=[self.stacks[0].stack_name],
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

    def test_command_info(self):
        from awstools.commands import cloudformation

        argh.dispatch_command(cloudformation.info,
                              argv=[self.stacks[0].stack_name],
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )
