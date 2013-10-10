# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import unittest

import boto


class TestFabric(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import awstools.fabric

        cls.roledefs = awstools.fabric.populate_roledefs()

        filters = {'instance-state-name': 'running'}
        reservations = boto.connect_ec2().get_all_instances(filters=filters)
        cls.instances = [i for r in reservations for i in r.instances]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_dict(self):
        self.assertIsInstance(self.roledefs, dict)

    def test_contains_lists(self):
        for key, value in self.roledefs.items():
            self.assertIsInstance(key, unicode)
            self.assertIsInstance(value, list)

    def test_check_instance_name(self):
        for instance in self.instances:
            if 'Name' in instance.tags:
                self.assertIn(instance.tags['Name'],
                              self.roledefs)

    def test_check_instance_altname(self):
        for instance in self.instances:
            if 'altName' in instance.tags:
                self.assertIn(instance.tags['altName'],
                              self.roledefs)

    def test_check_stack_name(self):
        for instance in self.instances:
            if 'aws:cloudformation:stack-name' in instance.tags:
                self.assertIn(instance.tags['aws:cloudformation:stack-name'],
                              self.roledefs)
