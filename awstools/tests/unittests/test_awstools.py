# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

from UserList import UserList
import unittest

import mock


class Stack(object):
    def __init__(self, name, status="CREATE_COMPLETE"):
        self.stack_name = name
        self.stack_status = status


class StackList(UserList):
    def __init__(self, data, next_token=None):
        super(StackList, self).__init__(data)
        self.next_token = next_token


class TestAwstools(unittest.TestCase):

    def setUp(self):
        self.teststacks1 = StackList(
            [Stack('test1'),  Stack('test2'), Stack('test3')],
            next_token='tok')

        self.teststacks2 = StackList(
            [Stack('ns1'), Stack('ns2'),
             Stack('deleted', status='DELETE_COMPLETE')])

        self.stack_list = sorted(['test1', 'test2', 'test3',
                                  'ns1', 'ns2', 'deleted'])

        self.result = None

    def check_slist(self, listok):
        self.assertEqual([s.stack_name for s in self.result], sorted(listok))

    @mock.patch('awstools.utils.cloudformation.boto.connect_cloudformation')
    def test_find_stacks_valid(self, mock_conn_cfn):
        from awstools.utils import cloudformation

        l_s = mock_conn_cfn.return_value.list_stacks
        l_s.side_effect = [self.teststacks1, self.teststacks2]

        self.result = cloudformation.find_stacks()

        l_s.assert_has_calls([mock.call(next_token=None),
                              mock.call(next_token='tok')])

        self.check_slist(['test1', 'test2', 'test3', 'ns1', 'ns2'])

    @mock.patch('awstools.utils.cloudformation.boto.connect_cloudformation')
    def test_find_stacks_valid_all(self, mock_conn_cfn):
        from awstools.utils import cloudformation

        l_s = mock_conn_cfn.return_value.list_stacks
        l_s.side_effect = [self.teststacks1, self.teststacks2]

        self.result = cloudformation.find_stacks(findall=True)

        l_s.assert_has_calls([mock.call(next_token=None),
                              mock.call(next_token='tok')])

        self.check_slist(['test1', 'test2', 'test3', 'ns1', 'ns2', 'deleted'])

    @mock.patch('awstools.utils.cloudformation.boto.connect_cloudformation')
    def test_find_stacks_pattern(self, mock_conn_cfn):
        from awstools.utils import cloudformation

        l_s = mock_conn_cfn.return_value.list_stacks
        l_s.side_effect = [self.teststacks1, self.teststacks2]

        self.result = cloudformation.find_stacks(pattern='ns')

        l_s.assert_has_calls([mock.call(next_token=None),
                              mock.call(next_token='tok')])

        self.check_slist(['ns1', 'ns2'])
