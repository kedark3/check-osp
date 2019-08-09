import os
import pytest
import random
import yaml
import yaycl
import yaycl_crypt

from osp_checks import CHECKS
from osp_logconf import get_logger
from wrapanapi.systems.openstack import OpenstackSystem


@pytest.fixture(scope="session")
def provider_data():
    if not os.path.exists("conf/cfme-qe-yamls"):
        pytest.fail("Please clone yamls directory in conf/ to run this test.")

    try:
        with open("conf/cfme-qe-yamls/complete/cfme_data.yaml", "r") as stream:
            cfme_data = yaml.safe_load(stream)
    except IOError:
        pytest.fail("CFME Data YAML file not found, no provider data available.")
    else:
        providers = cfme_data.get("management_systems")
        osp_providers = {
            key: providers[key] for key in list(providers.keys())
            if providers[key].get("type") == "openstack"
        }
        yield osp_providers.get(random.choice(list(osp_providers.keys())))

@pytest.fixture(scope="session")
def credentials(provider_data):
    if not os.path.exists("conf/.yaml_key"):
        pytest.fail("No yaml key in conf/.yaml_key")
    conf = yaycl.Config(
        "conf/cfme-qe-yamls/complete", crypt_key_file="conf/.yaml_key"
    )
    yaycl_crypt.decrypt_yaml(conf, "credentials", delete=False)
    try:
        with open("conf/cfme-qe-yamls/complete/credentials.yaml", "r") as stream:
            try:
                creds = yaml.safe_load(stream)
            except UnicodeDecodeError:
                os.remove("conf/cfme-qe-yamls/complete/credentials.yaml")
                pytest.fail(
                    "Unable to read decrypted credential file, "
                    "did you put the correct key in conf/.yaml_key?"
                )
            yield creds.get(provider_data.get("credentials"))
            # cleanup the file after the test finishes
            yaycl_crypt.encrypt_yaml(conf, "credentials", delete=True)
    except IOError:
        pytest.fail("Credential YAML file not found or not decrypted!")


@pytest.mark.parametrize("measurement", list(CHECKS.keys()))
def test_checks(provider_data, credentials, measurement):
    # get the necessary config
    measure_func = CHECKS[measurement]
    username, password = credentials.get("username"), credentials.get("password")
    logger = get_logger(True)

    system = OpenstackSystem(
        tenant=provider_data.get("tenant"),
        username=username,
        password=password,
        keystone_version=provider_data.get("keystone_version"),
        domain_id='default',
        auth_url=provider_data.get("auth_url")
    )

    # now try run the check
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        services = None
        if measurement == "services_status":
            # since this is a unit test, services don't matter
            services =  {
                'openstack-nova-api.service': 'Active: active (running)',
                'neutron-dhcp-agent.service': 'Active: active (running)'
            }
        measure_func(system, logger=logger, services=services)
    assert pytest_wrapped_e.type == SystemExit
