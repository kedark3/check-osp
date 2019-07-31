# coding: utf-8
"""
Helper functions
"""
from _socket import timeout

import paramiko


def is_service_in_status(ssh, name, expected_status):
    """Helper function for check_services_status to check a specific service's status"""
    stdin, stdout, stderr = ssh.exec_command("systemctl status {}".format(name))
    output = stdout.read()
    status = output.decode('utf-8').strip()
    return expected_status in status


def ssh_client(hostname, username, password):
    """
    SSH client with a workaround for using IPv4 addresses
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, timeout=60)
    return ssh
    if ssh.get_transport() is None:
        # An SSH Transport attaches to a stream (usually a socket), negotiates an encrypted session,
        # authenticates, and then creates stream tunnels, called channels, across the session.
        # If connection is not established, returns None.
        raise timeout("No pingable IP found")


def get_services_status_list(ssh):
    """
    This function fetches list of all units of type services from given host and returns in dict.

    systemctl command below returns output in following format:----->
    neutron-destroy-patch-ports.service loaded active exited  Neutron Destroy Patch Ports
    neutron-openvswitch-agent.service   loaded active running Neutron Open vSwitch Agent
    neutron-ovs-cleanup.service         loaded active exited  Neutron Open vSwitch Cleanup Utility
    awk command will slice it and conver it to this format:----->
    network.service: active (running)
    neutron-destroy-patch-ports.service: active (exited)
    neutron-openvswitch-agent.service: active (running)
    neutron-ovs-cleanup.service: active (exited)
    And the return statement has code to convert it to a dictionary of kind:----->
    {u'neutron-destroy-patch-ports.service': u' active (exited)',
    u'neutron-openvswitch-agent.service': u' active (running)',
    u'neutron-ovs-cleanup.service': u' active (exited)'}
    """

    stdin, stdout, stderr = ssh.exec_command("systemctl list-units --type service --all"
                                            " --no-page   --no-legend | "
                                            "awk -F ' ' '{print $1 \": \" $3 \" (\" $4\")\"}'")
    return {line.split(":")[0]: line.split(":")[1].replace("\n", "") for line in stdout.readlines()}
