# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ludia Inc.
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
# Author: Pior Bastida <pbastida@ludia.com>

import json
import os


class ErrorCfnTemplateNotFound(Exception):
    pass


class ErrorCfnTemplateInvalid(Exception):
    pass


class CfnParameters(list):
    def __init__(self, template, stack_info):
        for k, v in stack_info.iteritems():
            if k in template.parameters:
                self.append((k, v))

    def __repr__(self):
        return "\n".join([" %s = %s" % (k, v) for k, v in self])


class CfnTemplate(object):
    __repr = "<CfnTemplate[{0.version}] {0.description} from {0.path}>"

    def __init__(self, path):
        self.path = os.path.expanduser(path)
        try:
            self.body = open(self.path, 'rb').read()
        except IOError as e:
            raise ErrorCfnTemplateNotFound(e)
        try:
            self.json = json.loads(self.body)
        except ValueError as e:
            raise ErrorCfnTemplateInvalid(e)

    def __repr__(self):
        return self.__repr.format(self)

    def __str__(self):
        return self.body

    @property
    def parameters(self):
        if "Parameters" in self.json:
            return self.json["Parameters"].keys()
        else:
            return []

    @property
    def resources(self):
        return self.json["Resources"].keys()

    @property
    def description(self):
        return self.json["Description"]

    @property
    def version(self):
        return self.json["AWSTemplateFormatVersion"]

    @property
    def outputs(self):
        if "Outputs" in self.json:
            return self.json["Outputs"].keys()
        else:
            return []
