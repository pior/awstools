# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@socialludia.com>

import unittest

import mock
# import boto



class Stack(object):
    def __init__(self,
                 name="test",
                 status="CREATE_COMPLETE",
                 ):
        self.stack_name = name
        self.stack_status = status


class StackList(list):
    def __init__(self, l=[], next_token=None):
        self.extend(l)
        self.next_token = next_token

teststacks1 = StackList([
                        Stack('test1'),
                        Stack('test2'),
                        Stack('test3'),
                        ],
                        next_token='tok')

teststacks2 = StackList([
                        Stack('ns1'),
                        Stack('ns2'),
                        Stack('deleted', status='DELETE_COMPLETE')
                        ])

stack_list = sorted(['test1', 'test2', 'test3', 'ns1', 'ns2'])


class TestAwstools(unittest.TestCase):

    @mock.patch('boto.connect_cloudformation')
    def test_find_stacks_valid(self, mock_conn_cfn):
        from awstools import utils

        mock_cfn = mock.MagicMock()
        mock_cfn.list_stacks.side_effect = [
            teststacks1,
            teststacks2,
        ]
        mock_conn_cfn.return_value = mock_cfn

        res = utils.cloudformation.find_stacks()

        self.assertEqual(mock_cfn.list_stacks.mock_calls,
                         [mock.call(next_token=None),
                          mock.call(next_token='tok')]
                         )

        self.assertEqual(
            [s.stack_name for s in res],
            stack_list
        )
