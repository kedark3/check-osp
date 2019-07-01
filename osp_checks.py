# coding: utf-8
"""
These are the functions to check Red Hat OpenStack through the
OSP API/Wrapanapi
"""

import sys


def check_vm_count(system, warn=10, crit=15, **kwargs):
    """ Check overall host status. """
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

CHECKS={
    "vm_count": check_vm_count,
    }
