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

concurrent_input_sets = [
    {
        "name": "host-172-23-200-121",
        "subnet": ["172.23.200.121", "255.255.255.255"],
        "type": "ipmask"
    },
    {
        "name": "host-172-23-200-122",
        "subnet": ["172.23.200.122", "255.255.255.255"],
        "type": "ipmask"
    },
    {
        "name": "host-172-23-200-123",
        "subnet": ["172.23.200.123", "255.255.255.255"],
        "type": "ipmask"
    },
    {
        "name": "host-172-23-200-124",
        "subnet": ["172.23.200.124", "255.255.255.255"],
        "type": "ipmask"
    }
]


@pytest.fixture
def setup_params_concurrent(request):
    params_add = {
        "url": "/pm/config/adom/root/obj/firewall/address/",
        "data": [request.param]
    }
    params_delete = {
        "url": f"/pm/config/adom/root/obj/firewall/address/{request.param['name']}"
    }
    return config, params_add, params_delete


## write a test that will concurrently try to add and delete multiple address objects
@pytest.mark.parametrize("setup_params_concurrent", concurrent_input_sets, indirect=True)
def test_rpc_add_concurrent(setup_params_concurrent):
    config, params_add, params_delete = setup_params_concurrent

    response = operations['json_rpc_add'](config, params_add)

    assert response.get("status", None) == 0
    assert "add_response" in response, "Response missing 'add_response' key"
    assert response.get("add_response", {}).get("name", None) == params_add["data"][0][
        "name"], f"Expected name '{params_add['data'][0]['name']}' in response"

    response = operations['json_rpc_delete'](config, params_delete)
