# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@socialludia.com>

import unittest
from StringIO import StringIO

import yaml

from awstools import application

multiyaml = """
Application: appmodel
ShortName: am
KeyName: keymodel
live: false
environments:
    development:
        python:
            template: python.js
            AvailabilityZones: us-east-1a,us-east-1b,us-east-1c
            WebServerCapacity: 3
            InstanceType: c1.medium

---
Application: JustDevFromModel
ShortName: dm
model: appmodel
environments:
    development:
        python: True

---
Application: LiveApp
ShortName: dm
model: appmodel
live: true
environments:
    production:
        python: True

---
Application: MultiId
ShortName: mi
model: appmodel
live: false
environments:
    stage:
        node[1]:
            ident: node1
        node[2,3,4]:
            ident: node234
        node:
            ident: fallback

---
Application: test
ShortName: tt
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

data = yaml.load("""
Application: test
ShortName: tt
KeyName: keyname1
live: False
environments:
    stage:
        python: True
        java: True
        node[1]:
            ident: node1
        node[2,3,4]:
            ident: node234
        node:
            ident: default
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
""")


class TestApplicationApplication(unittest.TestCase):

    def setUp(self):
        self.app = application.Application(data)

    def test_application_application_base(self):
        self.assertEqual(self.app.name,
                         data['Application'])
        self.assertEqual(self.app.shortname,
                         data['ShortName'])
        self.assertEqual(self.app.live,
                         data['live'])
        self.assertEqual(self.app.environments,
                         data['environments'].keys())

    def test_application_application_validate_str(self):
        s = str(self.app)
        for k, v in data.items():
            if isinstance(v, str):
                self.assertIn(k, s)
                self.assertIn(v, s)

    def test_application_application_validate_ok(self):
        try:
            self.app.validate()
        except Exception as e:
            self.fail("validate() raised an exception for a valid ApplicationSettings\n"
                      "Exception: \n%s" % e)

    def test_application_application_validate_nok(self):
        for dropit in ['Application', 'ShortName', 'environments', 'live']:
            testdata = data.copy()
            del testdata[dropit]
            app = application.Application(testdata)

            with self.assertRaises(application.ApplicationInvalid):
                app.validate()

    def test_application_application_stackinfo_wrongapp(self):
        with self.assertRaises(application.ApplicationError):
            self.app.get_stack_info_from_stackname('xx-python-production')

    def test_application_application_stackinfo_wrongenv(self):
        with self.assertRaises(application.ApplicationEnvironmentNotFound):
            self.app.get_stack_info_from_stackname('tt-python-weirdenv')

    def test_application_application_stackinfo_wrongpool(self):
        with self.assertRaises(application.ApplicationPoolNotFound):
            self.app.get_stack_info_from_stackname('tt-wrongpool-production')

    def test_application_application_stackinfo_identifiers(self):
        gsifs = self.app.get_stack_info_from_stackname

        self.assertEqual(gsifs('tt-node-stage-1')['ident'], 'node1')
        self.assertEqual(gsifs('tt-node-stage-2')['ident'], 'node234')
        self.assertEqual(gsifs('tt-node-stage-3')['ident'], 'node234')
        self.assertEqual(gsifs('tt-node-stage-4')['ident'], 'node234')

    def test_application_application_stackinfo_identifier_default(self):
        gsifs = self.app.get_stack_info_from_stackname

        self.assertEqual(gsifs('tt-node-stage-notspecified')['ident'], 'default')

    def test_application_application_stackinfo(self):
        sinfo = self.app.get_stack_info_from_stackname('tt-python-production')

        valid_sinfo = {
            'Application': 'test',
            'AvailabilityZones': 'us-east-1a,us-east-1b,us-east-1c',
            'Environment': 'production',
            'InstanceType': 'c1.medium',
            'KeyName': 'keyname1',
            'ShortName': 'tt',
            'Type': 'python',
            'WebServerCapacity': 3,
            'live': False,
            'template': 'python.js',
        }

        self.assertDictEqual(sinfo, valid_sinfo)
