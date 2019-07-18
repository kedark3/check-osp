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
