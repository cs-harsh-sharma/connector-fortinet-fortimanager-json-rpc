### Testing the JSON RPC Connector

1. cd into the `tests` directory.
    ```bash
    cd fortimanager-json-rpc/tests
    ```
2. Rename the `.env.example` file 
    ```bash
    mv .env.example .env
    ```
3. Update the .env file with the required values to point to a FortiManager instance.
   - You must have a valid Hostname, Username, Password, and Port.
   - The FMG user must have read-write JSON API permissions.
4. Install the required packages.
    ```bash
    pip install -r requirements.txt
    ```
5. Run the following command to execute the tests.
   ```bash
   pytest --cov=fortinet-fortimanager-json-rpc 
   ```

- Sample output
   ```bash
    pytest --cov=fortinet-fortimanager-json-rpc --cov-report=html
   (.venv) dylanspille@dylanspille-mac fortimanager-json-rpc % pytest --cov=fortinet-fortimanager-json-rpc --cov-report=html
   =================================== test session starts =====================================
   platform darwin -- Python 3.12.3, pytest-8.2.1, pluggy-1.5.0
   rootdir: /Users/dylanspille/PycharmProjects/Github_FSR_Connectors/fortimanager-json-rpc
   plugins: cov-5.0.0
   collected 13 items                                    
   
   tests/test_fortimanager_rpc.py .............          [100%]
   
   ---------- coverage: platform darwin, python 3.12.3-final-0 ----------
   Coverage HTML written to dir htmlcov
   ```
   - Each dot represents a test that passed.

