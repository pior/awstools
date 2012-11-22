===================================
AWSTOOLS - high level tools for AWS
===================================

AWSTOOLS is a Python package that provide modules and commands to manage an infrastructure
on Amazon Web Services.

Awstools is driven by a set of conventions and choices to makes system operations simple to
the most. Awstools is mainly focused on managing multiple isolated social/web/mobile architectures.


Main conventions and choices:

- Using one of the Amazon Web Service is better than a custom solution
- Operation system: Ubuntu LTS or newer
- Configuration system: Puppet


At the moment awstools supports:

- Cloudformation smart management
  - ApplicationSettings (awstools.applications)
    Describe your application by declaring a set of :term:`Pool` per :term:`Environment`
  - cfn: List, Create, Update, Delete, Inspect


Installation
============

Python requirements:
 - argh
 - boto
 - PyYaml


Configuration
=============

| You must have a valid boto credentials provider to use the awstools.
| See the `Boto tutorial <http://docs.pythonboto.org/en/latest/boto_config_tut.html>`_.

- A configuration file is searched in this order:
  1. <specified by --config>
  2. ./awstools.cfg
  3. ~/.awstools.cfg
  4. /etc/awstools.cfg







