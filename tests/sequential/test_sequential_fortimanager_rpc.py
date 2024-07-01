"""
Copyright start
MIT License
Copyright (c) 2024 Fortinet Inc
Copyright end
"""

import importlib
import os
import sys

import pytest
from dotenv import load_dotenv

# Load environment variables from .env file in the parent directory
current_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
grandparent_directory = os.path.abspath(os.path.join(parent_directory, os.pardir))

# Add the grandparent directory to the system path
sys.path.insert(0, str(grandparent_directory))

env_path = os.path.join(parent_directory, '.env')
load_dotenv(dotenv_path=env_path)

# Import the module dynamically
module_name = "fortinet-fortimanager-json-rpc.operations"
my_package = importlib.import_module(module_name)

# Import the operations dictionary from the module
operations = my_package.operations

config = {
    "username": os.getenv("USERNAME"),
    "password": os.getenv("PASSWORD"),
    "address": os.getenv("ADDRESS"),
    "verify_ssl": os.getenv("VERIFY_SSL", "False").lower() in ("true", "1", "t"),
    "port": os.getenv("PORT"),
    "debug_connection": os.getenv("DEBUG_CONNECTION", "False").lower() in ("true", "1", "t"),
    "verbose_json": os.getenv("VERBOSE_JSON", "True").lower() in ("true", "1", "t"),
}


@pytest.fixture
def setup_params():
    params_add = {
        "url": "/pm/config/adom/root/obj/firewall/address/",
        "data": [{
            "name": "host-172-23-200-121",
            "subnet": [
                "172.23.200.121",
                "255.255.255.255"
            ],
            "type": "ipmask"
        }]
    }
    params_delete = {
        "url": "/pm/config/adom/root/obj/firewall/address/host-172-23-200-121"
    }
    return config, params_add, params_delete


def test_check_health():
    try:
        response = operations['check_health'](config)
        assert response, "Expected True for health check"
    except my_package.ConnectorError as e:
        assert False, f"Unexpected error: {e}"


def test_fail_check_health():
    try:
        bad_config = config.copy()
        bad_config['address'] = 'https://invalid-address'
        bad_config['port'] = "123"
        response = operations['check_health'](bad_config)
        assert False, "Expected error for invalid address"
    except my_package.ConnectorError:
        assert True, f"Expected error for invalid address"


def test_rpc_get():
    params = {"url": "/dvmdb/device"}
    response = operations['json_rpc_get'](config, params)
    # Status should be 0 for success
    assert response.get("status", None) == 0

    assert "get_response" in response, "Response missing 'get_response' key"


def test_rpc_get_invalid_url():
    params = {"url": "/dvmdb/devices", "data": ""}
    response = operations['json_rpc_get'](config, params)
    # Status should be 0 for success
    assert response.get("status", None) == -3, "Expected status -3 for invalid URL"

    assert "get_response" in response, "Response missing 'get_response' key"

    assert (response.get("get_response", {}).
            get("status", {}).
            get("message", {}) == "Object does not exist"), \
        "Expected message 'Object does not exist' for invalid URL"


def test_rpc_get_invalid_json():
    params = {"url": "/dvmdb/devices", "data": "{"}
    try:
        response = operations['json_rpc_get'](config, params)
    except my_package.ConnectorError as e:
        assert True, f"Expected error for invalid params"


def test_rpc_get_invalid_data():
    params = {"url": "/dvmdb/devices", "data": 123}
    try:
        response = operations['json_rpc_get'](config, params)
    except my_package.ConnectorError as e:
        assert True, f"Expected error for invalid params"


def test_rpc_get_no_params():
    params = {}
    for operation in operations:
        if operation != "check_health":
            try:
                response = operations[operation](config, params)
                assert False, f"Expected error for missing params for operation {operation}"
            except my_package.ConnectorError as e:
                assert True, f"Expected error for missing params for operation {operation}"


def test_rpc_get_invalid_config():
    invalid_config = config.copy()
    invalid_config["address"] = "https://invalid-address"
    params = {"url": "/dvmdb/device"}

    try:
        response = operations['json_rpc_get'](invalid_config, params)
    except Exception as e:
        assert isinstance(e, my_package.ConnectorError), "Expected ConnectorError for invalid config"


# Test the add operation by adding an address object
def test_rpc_add(setup_params):
    config, params_add, params_delete = setup_params
    response = operations['json_rpc_add'](config, params_add)
    # Status should be 0 for success
    assert response.get("status", None) == 0

    assert "add_response" in response, "Response missing 'add_response' key"

    assert response.get("add_response", {}).get("name",
                                                None) == "host-172-23-200-121", "Expected name 'host-172-23-200-121' in response"

    response = operations['json_rpc_delete'](config, params_delete)


def test_rpc_set(setup_params):
    config, params_add, params_delete = setup_params
    response = operations['json_rpc_add'](config, params_add)
    # Status should be 0 for success
    assert response.get("status", None) == 0

    assert "add_response" in response, "Response missing 'add_response' key"

    assert response.get("add_response", {}).get("name",
                                                None) == "host-172-23-200-121", "Expected name 'host-172-23-200-121' in response"
    params_set = {
        "url": params_delete["url"],
        "data": {
            # Ensure the name field is included
            "subnet": [
                "172.23.200.122",
                "255.255.255.255"
            ]
        }
    }
    response = operations['json_rpc_set'](config, params_set)

    assert response.get("status", None) == 0

    assert "set_response" in response, "Response missing 'set_response' key"

    response = operations['json_rpc_get'](config, params_delete)

    assert response.get("get_response", {}).get("subnet", [])[
               0] == "172.23.200.122", "Expected subnet[0] to be 172.23.200.122"

    response = operations['json_rpc_delete'](config, params_delete)


def test_rpc_delete(setup_params):
    config, params_add, params_delete = setup_params
    # First, run the add test
    response_add = operations['json_rpc_add'](config, params_add)
    assert response_add.get("status", None) == 0

    response = operations['json_rpc_delete'](config, params_delete)
    # Status should be 0 for success
    assert response.get("status", None) == 0

    assert "delete_response" in response, "Response missing 'delete_response' key"

    assert response.get("delete_response", {}).get("url",
                                                   None) == "/pm/config/adom/root/obj/firewall/address/host-172-23-200-121", "Expected url '/pm/config/adom/root/obj/firewall/address/host-172-23-200-121' in response"


def test_rpc_execute():
    # add a model device
    params = {
        "url": "/dvm/cmd/add/device",
        "data": {
            "adom": "root",
            "flags": [
                "create_task",
                "nonblocking"
            ],
            "device": {
                "mr": 4,
                "sn": "FGT60F0123456789",
                "name": "",
                "patch": 0,
                "os_ver": 6,
                "os_type": "fos",
                "mgmt_mode": "fmg",
                "meta fields": {
                    "Contact Email": "admin@test.com"
                },
                "device action": "add_model"
            }
        },
        "track_task": True
    }
    response = operations['json_rpc_execute'](config, params)
    # Status should be 0 for success
    assert response.get("status", None) == 0

    assert "execute_response" in response, "Response missing 'execute_response' key"

    assert "task_response" in response, "Response missing 'task_response' key"

    assert response.get("task_response", {}).get("percent", None) == 100, "Expected percent 100 in task response"

    # delete the device

    params = {
        "url": "/dvm/cmd/del/device",
        "data": {
            "data": {
                "adom": "root",
                "flags": [
                    "create_task",
                    "nonblocking"
                ],
                "device": "FGT60F0123456789"
            }
        },
        "track_task": True
    }
    response = operations['json_rpc_execute'](config, params)

    assert response.get("status", None) == 0

    assert "execute_response" in response, "Response missing 'execute_response' key"

    assert "task_response" in response, "Response missing 'task_response' key"

    assert response.get("task_response", {}).get("percent", None) == 100, "Expected percent 100 in task response"


def test_rpc_freeform():
    multi_data = []
    address_objects = [
        {"name": "host-172-23-200-121", "subnet": ["172.23.200.121", "255.255.255.255"]},
        {"name": "host-172-23-200-122", "subnet": ["172.23.200.122", "255.255.255.255"]},
        {"name": "host-172-23-200-123", "subnet": ["172.23.200.123", "255.255.255.255"]}
    ]

    for addr_obj in address_objects:
        multi_data.append({
            "url": "/pm/config/adom/root/obj/firewall/address/",
            "data": [addr_obj]
        })
    params = {
        "method": "add",
        "data": multi_data
    }

#     {
#         "method": "add",
#         "data": [
#             {
#                 "url": "/pm/config/adom/root/obj/firewall/address/",
#                 "data": [
#                     {
#                         "name": "host-172-23-200-121",
#                         "subnet": [
#                             "172.23.200.121",
#                             "255.255.255.255"
#                         ]
#                     }
#                 ]
#             },
#             {
#                 "url": "/pm/config/adom/root/obj/firewall/address/",
#                 "data": [
#                 ...
#

    response = operations['json_rpc_freeform'](config, params)

    assert "free_form_response" in response, "Response missing 'free_form_response' key"

    assert response.get("status") == 200, "Expected status 200 in response"

    assert len(response.get("free_form_response", [])) == len(
        address_objects), "Expected number of results to match number of address objects added"

    # delete the address objects
    params["method"] = "delete"
    multi_data = [{"url": f"/pm/config/adom/root/obj/firewall/address/{addr_obj['name']}"} for addr_obj in
                  address_objects]
    params["data"] = multi_data

    response = operations['json_rpc_freeform'](config, params)

    assert "free_form_response" in response, "Response missing 'free_form_response' key"

    assert response.get("status") == 200, "Expected status 200 in response"

    assert len(response.get("free_form_response", [])) == len(
        address_objects), "Expected number of results to match number of address objects added"
