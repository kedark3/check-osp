# coding: utf-8
"""
These are the functions to check Red Hat OpenStack through the
OSP API/Wrapanapi
"""

import sys


def check_vm_count(system, warn=10, crit=15, **kwargs):
    """ Check overall vm count. """
    warn = int(warn)
    crit = int(crit)
    vm_count = len(system.list_vms())
    # determine ok, warning, critical, unknown state
    if vm_count < warn:
        print("Ok: VM count is less than {}. VM Count = {}".format(warn, vm_count))
        sys.exit(0)
    elif vm_count >= warn and vm_count <= crit:
        print("Warning: VM count is >=  {} & <= {}. VM Count = {}"
            .format(warn, crit, vm_count))
        sys.exit(1)
    elif vm_count > crit:
        print("Critical: VM count is greate than crit. VM Count = {}".format(crit, vm_count))
        sys.exit(2)
    else:
        print("Unknown: VM count is unknown")
    sys.exit(3)


def check_keypair_count(system, warn=10, crit=15, **kwargs):
    """ Check overall keypair count. """
    warn = int(warn)
    crit = int(crit)
    keypair_count = len(system.list_keypair())
    # determine ok, warning, critical, unknown state
    if keypair_count < warn:
        print("Ok: Keypair count is less than {}. Keypair Count = {}".format(warn, keypair_count))
        sys.exit(0)
    elif keypair_count >= warn and keypair_count <= crit:
        print("Warning: Keypair count is >=  {} & <= {}. Keypair Count = {}"
            .format(warn, crit, keypair_count))
        sys.exit(1)
    elif keypair_count > crit:
        print("Critical: Keypair count is greate than crit. Keypair Count = {}".format(
            crit, keypair_count))
        sys.exit(2)
    else:
        print("Unknown: Keypair count is unknown")
    sys.exit(3)


def check_volume_count(system, warn=10, crit=15, **kwargs):
    """ Check overall volume count. """
    warn = int(warn)
    crit = int(crit)
    volume_count = len(system.list_volume())
    # determine ok, warning, critical, unknown state
    if volume_count < warn:
        print("Ok: Volume count is less than {}. Volume Count = {}".format(warn, volume_count))
        sys.exit(0)
    elif volume_count >= warn and volume_count <= crit:
        print("Warning: Volume count is >=  {} & <= {}. Volume Count = {}"
            .format(warn, crit, volume_count))
        sys.exit(1)
    elif volume_count > crit:
        print("Critical: Volume count is greate than crit. Volume Count = {}".format(
            crit, volume_count))
        sys.exit(2)
    else:
        print("Unknown: Volume count is unknown")
    sys.exit(3)


CHECKS = {
    "vm_count": check_vm_count,
    "keypair_count": check_keypair_count,
    "volume_count": check_volume_count
}
