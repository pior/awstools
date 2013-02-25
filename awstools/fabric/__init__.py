import boto

import awstools


DEFAULTTEMPLATES = u"""
    %(Name)s
    %(aws:cloudformation:stack-name)s
"""


def populate_roledefs():
    roledefs = {}

    config = awstools.read_config()
    cfg_roletmpl = unicode(config.get("fabric", "roletemplates",
                           DEFAULTTEMPLATES))
    roletemplates = [t.strip() for t in cfg_roletmpl.split('\n') if t.strip()]

    filters = {u'instance-state-name': u'running'}
    reservations = boto.connect_ec2().get_all_instances(filters=filters)
    instances = [i for r in reservations for i in r.instances]

    def add_instance(role, instance):
        roledefs.setdefault(role,
                            set()).add(instance.public_dns_name)
        roledefs.setdefault(u':'.join([role, instance.placement]),
                            set()).add(instance.public_dns_name)

    for instance in instances:
        for templates in roletemplates:
            try:
                add_instance(templates % instance.tags, instance)
            except:
                pass

    return dict([(k, list(v)) for k, v in roledefs.items()])
