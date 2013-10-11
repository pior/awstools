=====================================
 AWSTOOLS - high level tools for AWS
=====================================

AWSTOOLS is a Python package that provide modules and commands to manage an
infrastructure on `Amazon Web Services <http://aws.amazon.com>`_.

Awstools is driven by a set of conventions and choices to makes system
operations simple to the most. Awstools is mainly focused on managing multiple
isolated social/web/mobile architectures.


Main conventions and choices:

- Using one of the Amazon Web Service is better than a custom solution
- Operation system: Ubuntu LTS or newer
- Configuration system: `Puppet <http://puppetlabs.com>`_


At the moment awstools supports:

- `CloudFormation <http://aws.amazon.com/cloudformation>`_

   - **ApplicationSettings** (awstools.applications)
     Describe your application by declaring a set of *Pool* per *Environment*

   - **cfn**: List, Create, Update, Delete, Inspect
     Manage your AWS resources based on ApplicationSettings and cloudformation
     templates

- `EC2 <http://aws.amazon.com/ec2>`_

   - **ec2ssh**:
     Connect to one or multiple instances in a handy way

   - **awstools.fabric.populate_roledefs**:
     Populate Fabric roles with EC2 instances using the tags.
     fab -R App-Role cmd_run_on_all_app-role-*_instances



Installation
============

Python requirements:
 - argh
 - boto
 - PyYaml


Configuration
=============

::

   You must have a valid boto credentials provider to use the awstools.
   See the `Boto tutorial <http://docs.pythonboto.org/en/latest/boto_config_tut.html>`_.

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

Command ec2ssh
--------------

::

   $ ec2ssh MyInstanceByTagName
   Welcome to Ubuntu 12.04 LTS (GNU/Linux 3.2.0-23-virtual x86_64)

   ubuntu@tb-java-stage:~$


   $ ec2ssh MyInstanceByTagName uptime
    19:14:03 up 182 days,  4:49,  0 users,  load average: 0.08, 0.06, 0.05


   $ ec2ssh App-Role-* uptime
   ----- Command: uptime
   ----- Instances(2): App-Role-development,App-Role-production
   Confirm? (Y/n)
   ----- i-a0b24444: ec2-12-12-12-12.compute-1.amazonaws.com  10.101.101.101
    19:21:32 up 52 days,  3:51,  0 users,  load average: 0.00, 0.01, 0.05
   ----- i-ce786666: ec2-23-23-23-23.compute-1.amazonaws.com  10.201.201.201
    19:21:32 up 182 days,  4:56,  0 users,  load average: 0.08, 0.04, 0.05
   ----- DONE


   $ ec2ssh i-a0b24444 uptime
    19:24:28 up 52 days,  3:54,  0 users,  load average: 0.00, 0.01, 0.05


   $ ec2ssh 10.101.101.101 uptime
    19:25:18 up 52 days,  3:55,  0 users,  load average: 0.00, 0.01, 0.05


   $ ec2ssh App1-*,App2-*,App3-Role-test uptime


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

- **Report bugs**: https://bitbucket.org/pior/awstools/issues
- **Fork the code**: https://bitbucket.org/pior/awstools
- **Download**: http://pypi.python.org/pypi/awstools
