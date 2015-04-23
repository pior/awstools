Changelog for Awstools
======================


0.3.8 (2015-04-23)
------------------

- Nothing changed yet.


0.3.7 (2013-12-17)
------------------

- Fix wrong priority order when reading multiple configuration files


0.3.6 (2013-10-11)
------------------

- update author email
- cfnas: add subcommand metrics to control the ASG metrics collection


0.3.5 (2013-10-10)
------------------

- ec2ssh: add instance private hostname matching
- Move autoscale subcommands to a new cfnas command
- ec2ssh: add bash completion helpers
- Pylint


0.3.4 (2013-07-04)
------------------

- cfn batch-update: continue after a failure if user wants to


0.3.3 (2013-07-04)
------------------

- Add --force option to `cfn update` command
- Add a `cfn batch-update` command


0.3.2 (2013-06-11)
------------------

- Complete hgignore
- ec2ssh: enhance fallback when denying connection to multiple instances
- Fix wrong current_capacity displayed in autoscale update utility


0.3.1 (2013-03-13)
------------------

- fix *cfn setcapacity* setting 0 instead of the desired value


0.3 (2013-03-11)
----------------

- start using zest.releaser for versioning


0.2.3 (2013-02-01)
------------------

- display template description in cfn subcommands
- create subcommand "cfn activities"
