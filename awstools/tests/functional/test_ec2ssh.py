# -*- coding: utf-8 -*-
# Copyright (C) 2013 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@socialludia.com>

import time
import unittest
import StringIO

import mock
import argh
import boto

from awstools import commands


class TestEc2ssh(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ec2 = boto.connect_ec2()
        filters = {'instance-state-name': 'running'}
        reservations = cls.ec2.get_all_instances(filters=filters)
        cls.instances = [i for r in reservations for i in r.instances]

    def setUp(self):
        self.stdout = StringIO.StringIO()
        self.stderr = StringIO.StringIO()

    def tearDown(self):
        time.sleep(2)  # Protection against AWS api throttling

    def test_command_empty(self):
        argv = []
        argh.dispatch_command(commands.ec2ssh.connect,
                              argv=argv,
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        self.assertIn('CommandError', self.stderr.getvalue())

    @mock.patch('awstools.commands.ec2ssh.os.execvp')
    def test_command_id_single(self, mock_execvp):
        command = ['remote' 'command']
        identifiers = ','.join([self.instances[0].id])
        argv = [identifiers] + command

        argh.dispatch_command(commands.ec2ssh.connect,
                              argv=argv,
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        mock_execvp.assert_called_once_with(
            'ssh',
            ['ec2ssh', self.instances[0].public_dns_name] + command,
        )

    @mock.patch('awstools.commands.ec2ssh.argh.confirm')
    @mock.patch('awstools.commands.ec2ssh.subprocess.call')
    def test_command_id_multi(self, mock_call, mock_confirm):
        command = ['remote' 'command']
        identifiers = ','.join([self.instances[0].id,
                               self.instances[1].id])
        argv = [identifiers] + command

        argh.dispatch_command(commands.ec2ssh.connect,
                              argv=argv,
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        mock_call.assert_any_call(
            ['ssh', self.instances[0].public_dns_name] + command,
        )

        mock_call.assert_any_call(
            ['ssh', self.instances[1].public_dns_name] + command,
        )

        self.assertTrue(mock_confirm.called)
