# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import collections
import pprint
import re

import yaml


class ApplicationError(Exception):
    pass


class ApplicationInvalid(ApplicationError):
    pass


class ApplicationNotFound(ApplicationError):
    pass


class ApplicationEnvironmentNotFound(ApplicationNotFound):
    pass


class ApplicationPoolNotFound(ApplicationNotFound):
    pass


class Application(object):
    """
    Represents the properties of an application (direct and inherited from
    a model).
    """

    def __init__(self, properties):
        if not isinstance(properties, dict):
            raise ApplicationInvalid
        self.model = False
        self.properties = properties

    def __repr__(self):
        return '<Application %s>' % self.name

    def __str__(self):
        return pprint.pformat(self.properties)

    def apply_model(self, apps):
        if 'model' in self.properties:
            self.model = apps.get(name=self.properties['model'])

    def validate(self):
        for prop in ['name', 'shortname', 'environments', 'live']:
            try:
                getattr(self, prop)
            except KeyError as error:
                raise ApplicationInvalid("Missing properties: %s" % error)

    def _prop(self, prop):
        if prop in self.properties:
            return self.properties[prop]
        if self.model and prop in self.model.properties:
            return self.model.properties[prop]
        raise KeyError("Missing properties: %s" % prop)

    @property
    def name(self):
        return self._prop('Application')

    @property
    def shortname(self):
        return self._prop('ShortName')

    @property
    def live(self):
        return self._prop('live')

    @property
    def environments(self):
        return self.properties['environments'].keys()

    def get_stack_info_from_stackname(self, stackname):
        parts = stackname.split('-')
        if parts.pop(0) != self._prop("ShortName"):
            raise ApplicationError("Wrong application")
        pool = parts.pop(0)
        environment = parts.pop(0)
        try:
            identifier = parts.pop(0)
        except IndexError:
            identifier = None
        return self.get_stack_info(environment=environment,
                                   pool=pool,
                                   identifier=identifier)

    def get_stack_info(self, environment, pool, identifier=None):
        if environment not in self.environments:
            raise ApplicationEnvironmentNotFound(
                "No such environment: %s" % environment)

        # Seed the stack properties from model
        if self.model:
            try:
                stack_prop = self.model.get_stack_info(environment=environment,
                                                       pool=pool,
                                                       identifier=identifier)
            except ApplicationNotFound:
                stack_prop = {}
        else:
            stack_prop = {}

        # Update with application level properties
        stack_prop.update(self.properties)
        stack_prop.pop('environments')

        # Search for a matching pool/id
        pools = self.properties['environments'][environment]

        app_pool_prop = pools.get(pool)  # use default pool (without id)

        for pool_name, pool_props in pools.items():  # search matching id
            match = re.match(pool + r'\[(.+)\]', pool_name)
            if match:
                identifiers = [s.strip() for s in match.groups()[0].split(',')]
                if identifier in identifiers:
                    app_pool_prop = pool_props
                    break

        # Update with pool level properties
        # True as empty dict to get model properties only
        if app_pool_prop is True:
            app_pool_prop = {}
        if not isinstance(app_pool_prop, collections.Mapping):
            raise ApplicationPoolNotFound("No such pool: %s" % pool)
        stack_prop.update(app_pool_prop)

        # Update with actual environment/pool properties
        stack_prop.update({'Environment': environment,
                           'Type': pool})

        return stack_prop


class Applications(collections.Set):
    """
    Collection of Application
    """
    def __init__(self, yamldata=None):
        self._apps = []
        if yamldata:
            self.load_from_yaml(yamldata)

    def __iter__(self):
        return iter(self._apps)

    def __contains__(self, value):
        return value in self._apps

    def __len__(self):
        return len(self._apps)

    def __str__(self):
        return pprint.pformat(self._apps)

    def load_from_yaml(self, yamldata):
        """
        Load a set of Application definition from multiple document yaml stream
        """
        docs = yaml.load_all(yamldata)

        self._apps = [Application(d) for d in docs]

        for app in self:
            app.apply_model(self)
            app.validate()

    def get(self, name=None, shortname=None, stackname=None):
        """
        Return the first matching Application.
        Only compare the name or shortname even when matching with a stackname
        """
        if stackname:
            shortname = stackname.split('-')[0]

        for app in self:
            if name and app.name != name:
                continue
            if shortname and app.shortname != shortname:
                continue
            return app

        raise ApplicationNotFound("Application not found")
