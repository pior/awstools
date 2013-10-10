# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import unittest
import StringIO

import mock

from awstools import cfntemplate

CFNTEMPLATE_SKELETON = """{
    "AWSTemplateFormatVersion": "Version",
    "Description": "Description",
    "Parameters": {"Parameters": "Parameters"},
    "Resources": {"Resources": "Resources"}
}"""


class TestCfnTemplate(unittest.TestCase):

    def test_cfntemplate_cfnparameters(self):
        template = mock.Mock()
        template.parameters = ['un', 'deux', 'trois']
        stack_info = dict(zip(
            ['zero', 'un', 'deux', 'trois', 'quatre', 'cinq'],
            range(6)))

        result = [('un', 1), ('deux', 2), ('trois', 3)]

        param = cfntemplate.CfnParameters(template, stack_info)

        self.assertItemsEqual(param, result,
                              msg="The processed parameters are not valid")

        representation = repr(param)

        for key, value in result:
            self.assertRegexpMatches(
                representation, r'%s\s*=\s*%s' % (key, value),
                msg="The representation is invalid for key %s" % key)

    def test_cfntemplate_cfntemplate_open_error(self):
        with self.assertRaises(cfntemplate.ErrorCfnTemplateNotFound):
            cfntemplate.CfnTemplate('/doesnotexists')

    @mock.patch('__builtin__.open', create=True)
    @mock.patch('json.loads')
    def test_cfntemplate_cfntemplate_open_invalid(self, json_loads, mock_open):
        mock_open.return_value = mock.MagicMock(spec=file)
        json_loads.side_effect = ValueError

        with self.assertRaises(cfntemplate.ErrorCfnTemplateInvalid):
            cfntemplate.CfnTemplate('/buggytemplate')

    @mock.patch('__builtin__.open', create=True)
    @mock.patch('json.loads')
    def test_cfntemplate_cfntemplate_open_missing_keys(self, json_loads, mock_open):
        mock_open.return_value = mock.MagicMock(spec=file)
        mock_open.return_value.read.return_value = '{{'
        json_loads.return_value = {}

        template = cfntemplate.CfnTemplate('/realtemplate')

        self.assertIsInstance(template.parameters, list)

        with self.assertRaises(KeyError):
            _ = template.resources

        with self.assertRaises(KeyError):
            _ = template.description

        with self.assertRaises(KeyError):
            _ = template.version

        self.assertIsInstance(template.outputs, list)

    @mock.patch('__builtin__.open')
    def test_cfntemplate_cfntemplate_skeleton(self, mock_open):
        mock_open.return_value = StringIO.StringIO(
            CFNTEMPLATE_SKELETON)

        template = cfntemplate.CfnTemplate('/skeleton')
        self.assertEquals(template.parameters, ['Parameters'])
        self.assertEquals(template.description, 'Description')
        self.assertEquals(template.resources, ['Resources'])
        self.assertEquals(template.version, 'Version')
