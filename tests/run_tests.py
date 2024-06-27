import importlib
import os
import subprocess
import sys

from dotenv import load_dotenv

# Load environment variables from .env file in the parent directory
current_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))

# Add the grandparent directory to the system path
sys.path.insert(0, str(parent_directory))

# Load environment variables from .env file in the parent directory
env_path = os.path.join(current_directory, '.env')
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


def get_server_value():
    params = {
        "url": "/cli/global/system/global",
        "data": {"fields": ["workspace-mode", "adom-status"]}
    }
    response = operations['json_rpc_get'](config, params)
    # Status should be 0 for success
    assert response.get("status", None) == 0

    assert "get_response" in response, "Response missing 'get_response' key"
    workspace_mode = response['get_response']['workspace-mode']
    print(f"Current workspace mode: {workspace_mode}")
    if workspace_mode in [0, "0", "disabled"]:
        return 0
    else:
        return 1


def update_server_value(new_value):
    params = {
        "url": "/cli/global/system/global",
        "data": {"workspace-mode": new_value}
    }
    print("Setting workspace mode to", new_value)
    response = operations['json_rpc_set'](config, params)
    # Status should be 0 for success
    assert response.get("status", None) == 0

    assert "set_response" in response, "Response missing 'set_response' key"


def execute_tests():
    # Run sequential tests
    result = subprocess.run(["pytest", "sequential"], check=True)
    if result.returncode != 0:
        print("Sequential tests failed")
        return result.returncode

    # Run concurrent tests with 4 workers
    result = subprocess.run(["pytest", "concurrent", "-n", "4", '-v'], check=True)
    if result.returncode != 0:
        print("Concurrent tests failed")
        return result.returncode

    print("All tests passed")


def run_tests():
    original_value = get_server_value()
    new_value = 1 if original_value == 0 else 0
    execute_tests()
    update_server_value(new_value)
    execute_tests()
    update_server_value(original_value)


if __name__ == "__main__":
    exit(run_tests())
