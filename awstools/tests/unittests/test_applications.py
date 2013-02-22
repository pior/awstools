# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@socialludia.com>

import unittest

import yaml
import mock

from awstools import application


datayaml = """
Application: test
ShortName: tt
KeyName: keyname1
model: base
live: False
environments:
    stage:
        python: True
        java: True
    production:
        cloudadmin:
            template: cloudadmin.js
            InstanceType: m1.small
        python:
            template: python.js
            AvailabilityZones: us-east-1a,us-east-1b,us-east-1c
            WebServerCapacity: 3
            InstanceType: c1.medium
        java:
            template: java.js
            AvailabilityZones: us-east-1a,us-east-1b
            WebServerCapacity: 2
            InstanceType: c1.medium

---

Application: base
ShortName: ba
KeyName: keyname1
live: False
environments:
    stage:
        python: True
        java: True
    production:
        cloudadmin:
            template: cloudadmin.js
            InstanceType: m1.small
        python:
            template: python.js
            AvailabilityZones: us-east-1a,us-east-1b,us-east-1c
            WebServerCapacity: 3
            InstanceType: c1.medium
        java:
            template: java.js
            AvailabilityZones: us-east-1a,us-east-1b
            WebServerCapacity: 2
            InstanceType: c1.medium
"""
data = yaml.load_all(datayaml)


class TestApplicationsLoading(unittest.TestCase):

    def test_instantiate(self):
        try:
            self.app = application.Applications()
        except Exception as e:
            self.fail("Failed to instanciate: %s" % e)

        try:
            str(self.app)
        except Exception as e:
            self.fail("Failed to call __str__: %s" % e)

    def test_load_from_yaml_valid(self):
        self.app = application.Applications()

        try:
            self.app.load_from_yaml(datayaml)
        except Exception as e:
            self.fail("Failed to load valid yaml data: %s" % e)

    def test_load_from_yaml_invalid_yaml(self):
        self.app = application.Applications()

        with self.assertRaises(yaml.parser.ParserError):
            self.app.load_from_yaml("][")

    def test_load_from_yaml_invalid_app(self):
        self.app = application.Applications()

        with self.assertRaises(application.ApplicationInvalid):
            self.app.load_from_yaml("---")


class TestApplications(unittest.TestCase):

    @mock.patch('awstools.application.yaml')
    @mock.patch('awstools.application.Application', create=True)
    def test_load_from_yaml(self, mock_app, mock_yaml):
        from awstools.application import Applications
        mock_yaml.load_all.return_value = ['app1', 'app2']

        apps = Applications()
        apps.load_from_yaml("NotNone")

        mock_app.assert_any_call('app1')
        mock_app.assert_any_call('app2')

        for app in apps:
            self.assertTrue(app.apply_model.called,
                            msg="Application.apply_model() not called")
            self.assertTrue(app.validate.called,
                            msg="Application.validate() not called")

    def test_get(self):
        from awstools.application import Applications

        mock_app_un = mock.Mock(shortname='u')
        mock_app_un.name = 'un'
        mock_app_deux = mock.Mock(shortname='d')
        mock_app_deux.name = 'deux'
        mock_app_trois = mock.Mock(shortname='t')
        mock_app_trois.name = 'trois'

        apps = Applications()
        apps._apps = [
            mock_app_un,
            mock_app_deux,
            mock_app_trois
        ]

        self.assertItemsEqual(
            apps,
            [mock_app_un, mock_app_deux, mock_app_trois],
            msg="Applications don't behave like a set"
        )

        self.assertIs(apps.get(name='un'),
                      mock_app_un)
        self.assertIs(apps.get(shortname='u'),
                      mock_app_un)
        self.assertIs(apps.get(name='deux'),
                      mock_app_deux)
        self.assertIs(apps.get(shortname='d'),
                      mock_app_deux)

    def test_get_notfound(self):
        from awstools.application import (
            Applications,
            ApplicationNotFound
        )

        apps = Applications()

        with self.assertRaises(ApplicationNotFound):
            apps.get(name='nada')
