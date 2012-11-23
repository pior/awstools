=====================================
 AWSTOOLS - high level tools for AWS
=====================================

AWSTOOLS is a Python package that provide modules and commands to manage an infrastructure
on `Amazon Web Services <http://aws.amazon.com>`_.

Awstools is driven by a set of conventions and choices to makes system operations simple to
the most. Awstools is mainly focused on managing multiple isolated social/web/mobile architectures.


Main conventions and choices:

- Using one of the Amazon Web Service is better than a custom solution
- Operation system: Ubuntu LTS or newer
- Configuration system: `Puppet <http://puppetlabs.com>`_


At the moment awstools supports:

- `CloudFormation <http://aws.amazon.com/cloudformation>`_ smart management
  - **ApplicationSettings** (awstools.applications)
    Describe your application by declaring a set of *Pool* per *Environment*
  - **cfn**: List, Create, Update, Delete, Inspect
    Manage your AWS resources based on ApplicationSettings and cloudformation templates


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

- A **configuration file** is searched in this order:
  1. <specified by --config>
  2. ./awstools.cfg
  3. ~/.awstools.cfg
  4. /etc/awstools.cfg

- An application settings file is searched in this order:
  1. specified by --settings
  2. specified by awstools configuration file


Testing
=======

Run the test with nose

::
    pip install -r requirements-test.txt
    nosetests


Examples
========

Configuration
-------------

::

   [cfn]
   settings = ~/cloudformation/applications.yaml
   templatedir = ~/cloudformation


Applications Settings
---------------------

::

   Application: gmail
   ShortName: gm
   KeyName: google-secretkey
   live: True
   environments:
     production:
       storage:
         template: storage.js
         AvailabilityZones: us-east-1a,us-east-1b,us-east-1c
         WebServerCapacity: 6
         InstanceType: m1.xlarge
       frontweb:
         template: frontweb.js
         AvailabilityZones: us-east-1a,us-east-1b
         WebServerCapacity: 4
         InstanceType: m1.medium
     stage:
       storage:
         template: storage.js
         AvailabilityZones: us-east-1a,us-east-1b
         WebServerCapacity: 2
         InstanceType: m1.small
       frontweb:
         template: frontweb.js
         AvailabilityZones: us-east-1a,us-east-1b
         WebServerCapacity: 2
         InstanceType: m1.small
     test:
       frontweb:
         template: frontweb.js
         AvailabilityZones: us-east-1a,us-east-1b
         WebServerCapacity: 2

The application *gmail* has a production, a staging and a test environment.
An environment is defined by two pools: *storage* and *frontweb*.
However in test you mock the storage and don't need a *storage* pool.
All those settings will be available for the CloudFormation templates.



Contribute
==========

Want to contribute, report a but of request a feature ? The development goes on
at Ludia's BitBucket account:

- **Report bugs**: https://bitbucket.org/Ludia/awstools/issues
- **Fork the code**: https://bitbucket.org/Ludia/awstools
- **Download**: http://pypi.python.org/pypi/awstools
