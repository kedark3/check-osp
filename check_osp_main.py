#!/usr/bin/env python
# coding: utf-8
"""
This script performs checks for Red Hat OpenStack hosts/Manager through the
RHV API.
"""

import argparse
import sys

from argparse import RawTextHelpFormatter
from osp_checks import CHECKS
from wrapanapi.systems.openstack import OpenstackSystem


def get_measurement(measurement):
    return CHECKS.get(measurement, None)


def main():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-o",
        "--osp-auth-url",
        dest="auth_url",
        help="Auth URL for OSP",
        type=str
    )
    parser.add_argument(
        "-t",
        "--tenant",
        dest="tenant",
        help="Tenant name",
        type=str
    )
    parser.add_argument(
        "-u",
        "--username",
        dest="user",
        help="remote user to use",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        help="password for Openstack",
        type=str
    )
    parser.add_argument(
        "-k",
        "--keystone-version",
        dest="keystone_ver",
        help="keystone version for Openstack",
        type=int,
        default=3
    )
    parser.add_argument(
        "-m",
        "--measurement",
        dest="measurement",
        help="Type of measurement to carry out",
        type=str
    )
    parser.add_argument(
        "-w",
        "--warning",
        dest="warning",
        help="Warning value. Could be fraction or whole number.",
        type=float,
        default=0.75
    )
    parser.add_argument(
        "-c",
        "--critical",
        dest="critical",
        help="Critical value. Could be fraction or whole number.",
        type=float,
        default=0.9
    )
    args = parser.parse_args()
    if float(args.warning) > float(args.critical):
        print("Error: warning value can not be greater than critical value")
        sys.exit(3)

    # connect to the system
    # we can remove keystone_version arg if my PR is https://github.com/ManageIQ/wrapanapi/pull/395
    # is merged into wrapanapi
    system = OpenstackSystem(tenant=args.tenant, username=args.user, password=args.password,
    keystone_version=args.keystone_ver, domain_id='default', auth_url=args.auth_url)
    # get measurement function
    measure_func = get_measurement(args.measurement)
    if not measure_func:
        print("Error: measurement {} not understood".format(args.measurement))
        sys.exit(3)
    # run the measurement function
    measure_func(system, warn=args.warning, crit=args.critical)


if __name__ == "__main__":
    main()
