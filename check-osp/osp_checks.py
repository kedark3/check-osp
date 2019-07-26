# coding: utf-8
"""
These are the functions to check Red Hat OpenStack through the
OSP API/Wrapanapi
"""

import sys

from utils import get_services_status_list
from utils import ssh_client


def check_vm_count(system, warn=10, crit=15, **kwargs):
    """ Check overall vm count. """
    logger = kwargs["logger"]
    warn = int(warn)
    crit = int(crit)
    vm_count = len(system.list_vms())
    # determine ok, warning, critical, unknown state
    if vm_count < warn:
        msg = ("Ok: VM count is less than {}. VM Count = {}".format(warn, vm_count))
        logger.info(msg)
        print(msg)
        sys.exit(0)
    elif vm_count >= warn and vm_count <= crit:
        msg = ("Warning: VM count is >=  {} & <= {}. VM Count = {}"
            .format(warn, crit, vm_count))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif vm_count > crit:
        msg = ("Critical: VM count is greater than {}. VM Count = {}".format(crit, vm_count))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    else:
        print("Unknown: VM count is unknown")
    sys.exit(3)


def check_keypair_count(system, warn=10, crit=15, **kwargs):
    """ Check overall keypair count. """
    logger = kwargs["logger"]
    warn = int(warn)
    crit = int(crit)
    keypair_count = len(system.list_keypair())
    # determine ok, warning, critical, unknown state
    if keypair_count < warn:
        msg = "Ok: Keypair count is less than {}. Keypair Count = {}".format(warn, keypair_count)
        logger.info(msg)
        print(msg)
        sys.exit(0)
    elif keypair_count >= warn and keypair_count <= crit:
        msg = ("Warning: Keypair count is >=  {} & <= {}. Keypair Count = {}"
            .format(warn, crit, keypair_count))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif keypair_count > crit:
        msg = ("Critical: Keypair count is greater than {}. Keypair Count = {}".format(
            crit, keypair_count))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    else:
        msg = ("Unknown: Keypair count is unknown")
        logger.info(msg)
        print(msg)
    sys.exit(3)


def check_volume_count(system, warn=10, crit=15, **kwargs):
    """ Check overall volume count. """
    logger = kwargs["logger"]
    warn = int(warn)
    crit = int(crit)
    volume_count = len(system.list_volume())
    # determine ok, warning, critical, unknown state
    if volume_count < warn:
        msg = ("Ok: Volume count is less than {}. Volume Count = {}".format(warn, volume_count))
        logger.info(msg)
        print(msg)
        sys.exit(0)
    elif volume_count >= warn and volume_count <= crit:
        msg = ("Warning: Volume count is >=  {} & <= {}. Volume Count = {}"
            .format(warn, crit, volume_count))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif volume_count > crit:
        msg = ("Critical: Volume count is greater than {}. Volume Count = {}".format(
            crit, volume_count))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    else:
        msg = ("Unknown: Volume count is unknown")
        logger.info(msg)
        print(msg)
    sys.exit(3)


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
        try:
            service_for_host = services[host]
            with ssh_client(host, username="root", password=system.password) as ssh:
                service_status_dict = get_services_status_list(ssh)
        except KeyError:
            logger.info("Skipping host {} as it is not in yml.".format(host))
            continue
        for service_name, expected_status in service_for_host.items():
            # if service_status_dict has service `service_name` get its status
            # compare it with expected_status
            try:
                logger.debug("service:{} status: {} expected_status: {}"
                    .format(service_name, service_status_dict[service_name], expected_status))
                service_status = (expected_status in service_status_dict[service_name])
            except KeyError:
                # This is because not all hosts may have all services installed
                logger.debug("Service {} not found on host {}".format(service_name, host))
                continue
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
