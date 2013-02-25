import re
from fnmatch import fnmatch

import boto
import boto.ec2


def get_instances(region='us-east-1',
                  filters={'instance-state-name': 'running'},
                  instance_ids=None):

    ec2 = boto.connect_ec2(region=boto.ec2.get_region(region))

    reservations = ec2.get_all_instances(filters=filters,
                                         instance_ids=instance_ids)

    return [i for r in reservations for i in r.instances]


def get_name(instance):
    name = instance.tags.get('Name')
    altname = instance.tags.get('altName')
    instanceid = instance.id
    return name or altname or instanceid


def filter_instances(specifiers, instances):
    targets = set()

    RE_INSTANCE_ID = re.compile('^i-[a-f0-9]{8}$', re.IGNORECASE)
    RE_PRIVATE_IP = re.compile('^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    for instance in instances:

        for specifier in specifiers:

            if re.match(RE_INSTANCE_ID, specifier):
                if instance.id == specifier:
                    targets.add(instance)

            elif re.match(RE_PRIVATE_IP, specifier):
                if instance.private_ip_address == specifier:
                    targets.add(instance)

            else:
                name = instance.tags.get('Name', '').lower()
                altname = instance.tags.get('altName', '').lower()

                if fnmatch(name, specifier.lower()):
                    targets.add(instance)
                elif fnmatch(altname, specifier.lower()):
                    targets.add(instance)

    return list(targets)
