# -*- coding: utf-8 -*-
# Copyright (C) 2013 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import unittest
import StringIO

import mock
import argh


class TestEc2ssh(unittest.TestCase):

    def setUp(self):
        self.stdout = StringIO.StringIO()
        self.stderr = StringIO.StringIO()

        def get_ec2instance_mock(i):
            ec2imock = mock.Mock()
            ec2imock.id = 'id-%s' % i
            ec2imock.tags.get.return_value = 'name-%s' % i
            ec2imock.public_dns_name = 'public-dns-%s' % i
            ec2imock.private_dns_name = 'private-dns-%s' % i
            ec2imock.state = 'running'
            return ec2imock
        self.instances = [get_ec2instance_mock(i) for i in range(10)]

    def test_command_empty(self):
        from awstools.commands import ec2ssh

        argv = []
        argh.dispatch_command(ec2ssh.connect,
                              argv=argv,
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        self.assertIn('CommandError', self.stderr.getvalue())

    @mock.patch('awstools.commands.ec2ssh.ec2')
    @mock.patch('awstools.commands.ec2ssh.os.execvp')
    def test_command_single(self, mock_execvp, mock_ec2):
        from awstools.commands import ec2ssh

        command = ['remote', 'command']
        identifiers = self.instances[0].id

        mock_ec2.get_instances.return_value = self.instances
        mock_ec2.get_name = lambda x: x.id
        mock_ec2.filter_instances = lambda x, y: [y[0]]

        argv = [identifiers] + command
        argh.dispatch_command(ec2ssh.connect,
                              argv=argv,
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        mock_execvp.assert_called_once_with(
            'ssh',
            ['ec2ssh', self.instances[0].public_dns_name] + command,
        )

    @mock.patch('awstools.commands.ec2ssh.ec2')
    @mock.patch('awstools.commands.ec2ssh.argh.confirm')
    @mock.patch('awstools.commands.ec2ssh.subprocess.call')
    def test_command_multi(self, mock_call, mock_confirm, mock_ec2):
        from awstools.commands import ec2ssh

        command = ['remote' 'command']
        identifiers = ','.join([self.instances[0].id,
                                self.instances[1].id])

        mock_ec2.get_instances.return_value = self.instances
        mock_ec2.get_name = lambda x: x.id
        mock_ec2.filter_instances = lambda x, y: [y[0], y[1]]

        argv = [identifiers] + command
        argh.dispatch_command(ec2ssh.connect,
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

    def test_option_completion_script(self):
        from awstools.commands import ec2ssh

        argv = ['--completion-script']
        argh.dispatch_command(ec2ssh.connect,
                              argv=argv,
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        self.assertIn('_ec2ssh()', self.stdout.getvalue())
        self.assertIn('ec2ssh --completion-list', self.stdout.getvalue())
        self.assertIn('complete -F _ec2ssh ec2ssh', self.stdout.getvalue())

    @mock.patch('awstools.commands.ec2ssh.ec2')
    @mock.patch('awstools.commands.ec2ssh.read_completion_list')
    def test_option_completion_list(self, mock_read, mock_ec2):
        from awstools.commands import ec2ssh

        mock_read.return_value = ['instance_name', 'instance_name2']

        argv = ['--completion-list']
        argh.dispatch_command(ec2ssh.connect,
                              argv=argv,
                              output_file=self.stdout,
                              errors_file=self.stderr,
                              completion=False,
                              )

        self.assertIn(' '.join(mock_read.return_value), self.stdout.getvalue())

    def test_completion_list(self):
        from awstools.commands import ec2ssh

        ec2ssh.write_completion_list(self.instances)
        compl_list = ec2ssh.read_completion_list()

        self.assertItemsEqual(compl_list,
                              [i.tags.get() for i in self.instances])

