# coding: utf-8
"""
These are the functions to check Red Hat OpenStack through the
OSP API/Wrapanapi
"""

import sys

from utils import is_service_in_status
from utils import ssh_client


def check_threshold(count, warn, crit, logger):
    """determine ok, warning, critical, unknown state. """
    warn = int(warn)
    crit = int(crit)
    if count < warn:
        msg = ("Ok: Resource Count={} is less than threshold warning={}".format(count), warn)
        logger.info(msg)
        print(msg)
        sys.exit(0)
    elif count >= warn and count <= crit:
        msg = ("Warning: Resource count={} is reached threshold warning range={}<-->{}".format(
            count, warn, crit))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif count > crit:
        msg = ("Critical: Resource count={} has crossed threshold critical={}".format(
            count, crit))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    else:
        print("Unknown: Resource count is unknown")
    sys.exit(3)


def check_vm_count(system, warn=10, crit=15, **kwargs):
    """ Check overall vm count. """
    logger = kwargs["logger"]
    vm_count = len(system.list_vms())
    logger.info("Checking threshold status for instance count")
    check_threshold(vm_count, warn, crit, logger)


def check_keypair_count(system, warn=10, crit=15, **kwargs):
    """ Check overall keypair count. """
    logger = kwargs["logger"]
    keypair_count = len(system.list_keypair())
    logger.info("Checking threshold status for keypair count")
    check_threshold(keypair_count, warn, crit, logger)


def check_volume_count(system, warn=10, crit=15, **kwargs):
    """ Check overall volume count. """
    logger = kwargs["logger"]
    volume_count = len(system.list_volume())
    logger.info("Checking threshold status for volume count")
    check_threshold(volume_count, warn, crit, logger)


def check_snapshot_count(system, warn=10, crit=15, **kwargs):
    """ Check overall Snapshot count. """
    logger = kwargs["logger"]
    snapshot_count = 0
    images = system.list_templates()
    for img in images:
        if img.name.startswith("test_snapshot_"):
            snapshot_count += 1
    logger.info("Checking threshold status for snapshot count")
    check_threshold(snapshot_count, warn, crit, logger)


def check_services_status(system, **kwargs):
    """Check to see if service are in the desired state"""
    logger = kwargs["logger"]
    hosts = list(set([host.host_name for host in system.api.hosts.list()]))
    hosts_agents = dict()
    hosts_status = dict()
    services = kwargs['services']

    for host in hosts:
        # if a hostname contains localhost, we want to avoid trying to connect
        if 'localhost' in host:
            continue
        ssh = ssh_client(host, username="root", password=system.password)
        with ssh:
            for service_name, status in services.iteritems():
                service_status = is_service_in_status(ssh, service_name, status)
                try:
                    hosts_agents[host].update({service_name: service_status})
                except KeyError:
                    hosts_agents[host] = {service_name: service_status}

        hosts_status[host] = all(hosts_agents[host].values())

    overall_status = all(hosts_status.values())

    if overall_status:  # all true, everything is running
        msg = ("Ok: all services {} are in the desired state on all hosts".format(services.keys()))
        logger.info(msg)
        print(msg)
        sys.exit(0)
    else:
        trouble_hosts = [host for host, status in hosts_status.iteritems() if not status]
        msg = ("Critical: These hosts don't have all agents in the desired state: {}."
               "Overall status is {} (where False means not in desired state)"
               .format(trouble_hosts, hosts_agents))
        logger.error(msg)
        print(msg)
        sys.exit(2)


CHECKS = {
    "vm_count": check_vm_count,
    "keypair_count": check_keypair_count,
    "volume_count": check_volume_count,
    "services_status": check_services_status
}
