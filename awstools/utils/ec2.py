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



RE_INSTANCE_ID = re.compile(r'^i-[a-fA-F0-9]{8}$')
RE_PRIVATE_IP = re.compile(r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
RE_PRIVATE_HOSTNAME_1 = re.compile(r'^ip-10(-\d{1,3}){3}')
RE_PRIVATE_HOSTNAME_2 = re.compile(r'^domU(-[0-9a-fA-F]{2}){6}')


def filter_instances(specifiers, instances):
    targets = set()

    for instance in instances:
        for specifier in specifiers:

            if re.match(RE_INSTANCE_ID, specifier):
                if instance.id == specifier:
                    targets.add(instance)

            elif re.match(RE_PRIVATE_IP, specifier):
                if instance.private_ip_address == specifier:
                    targets.add(instance)

            elif re.match(RE_PRIVATE_HOSTNAME_1, specifier):
                if instance.private_dns_name.startswith(specifier):
                    targets.add(instance)

            elif re.match(RE_PRIVATE_HOSTNAME_2, specifier):
                if instance.private_dns_name.startswith(specifier):
                    targets.add(instance)

            else:
                name = instance.tags.get('Name', '').lower()
                altname = instance.tags.get('altName', '').lower()

                if fnmatch(name, specifier.lower()):
                    targets.add(instance)
                elif fnmatch(altname, specifier.lower()):
                    targets.add(instance)

    return list(targets)
