#!/usr/bin/python3
#
# MIT License
#
# (C) Copyright 2025 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

"""
Discover physical racks along with corresponding
management nodes (master, worker and storage).
"""

import json
import subprocess
from collections import defaultdict
import base64
import sys
from typing import Union

import requests

# Define the endpoint URL
hsm_url = "https://api-gw-service-nmn.local/apis/smd/hsm/v2/State/Components"
sls_url= "https://api-gw-service-nmn.local/apis/sls/v1/search/hardware"

# Run the kubectl command to get the secret 
def token_fetch() ->  Union[str, None]:
    """
    Fetch the keycloak token.
    Return keycloak token.
    """
    response = None

    try:
        result = subprocess.run(
            ["kubectl", "get", "secrets", "admin-client-auth", "-o", "jsonpath={.data.client-secret}"],
            stdout=subprocess.PIPE,  # Capture stdout
            stderr=subprocess.PIPE,  # Capture stderr
            universal_newlines=True,  # Use text mode for output decoding
            check=True,  # Will raise an exception if the command fails
        )
        # If the command was successful, result will be a CompletedProcess object
        client_secret = base64.b64decode(result.stdout.strip()).decode('utf-8')

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running kubectl: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

    # Set up the parameters and URL to make the POST request
    url = "https://api-gw-service-nmn.local/keycloak/realms/shasta/protocol/openid-connect/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": "admin-client",
        "client_secret": f"{client_secret}",
    }

    # Make the API request to get the token
    response = requests.post(url, data=data)

    # Get the json output
    token = response.json()
    token = token.get("access_token")
    return token

def rack_info(hsm_response: requests.Response, sls_response: requests.Response) -> None:
    """
    Get/ extract  management racks and corresponding management nodes (master, worker and storage)
    from HSM and SLS.
    hsm_response: Response for GET request to HSM endpoint
    sls_response: Response for GET request to SLS endpoint
    Group and write rack to management nodes mapping into to file /tmp/rack_info.txt, to be consumed
    by zoning functions (k8s and ceph).
    Returns nothing.
    """
    # Convert the hsm and sls data into json format
    hsm_data = hsm_response.json()
    sls_data = sls_response.json()

    # Check the response status and print the JSON output
    if hsm_response.status_code == 200:
        filtered_data = [component for component in hsm_data["Components"] if component.get("Role") == "Management" and component.get("SubRole") == "Master" or component.get("SubRole") == "Worker" or component.get("SubRole") == "Storage"]

         # Group by rack ID (extracted from "ID")
        res_rack = defaultdict(list)

        for component in filtered_data:
            rack_id = component["ID"].split("c")[0]  # Extract "x3000" from "x3000c0s1b75n75"
            for sls_entry in sls_data:
                if sls_entry["Xname"] == component["ID"]:
                    aliases = sls_entry["ExtraProperties"]["Aliases"][0]
                    res_rack[rack_id].append(aliases)
        res_rack = json.dumps(res_rack, indent=4)
        print(res_rack)
        # Redirecting the result to the tmp file
        with open("/tmp/rack_info.txt", "w") as file:
            file.write(res_rack + "\n")
    else:
        print(f"Failed to access the endpoint. Status code: {hsm_response.status_code}")
        print("Response text:", hsm_response.text)

def main() -> None:
    """
    Discover/ fetch/ group management racks and corresponding mapped management nodes
    info (xnames in the form of key value pair) from HSM and SLS and store it under
    /tmp/rack_info.txt file to be consumed by zoning(k8s and ceph) functions.
    """
    # Fetch the keycloak token
    token = token_fetch()
    if token is None:
        print("Failed to get the keycloak token")
        sys.exit(1)

    # Parameters for sls
    params = {'type': 'comptype_node'}
    headers = {
        "Authorization": f"Bearer {token}",  # Add the token as a Bearer token
        "Accept": "application/json"         # Indicate you want a JSON response
    }

    # Make the GET request to hsm and sls enpoints
    hsm_response = requests.get(hsm_url, headers=headers)
    sls_response = requests.get(sls_url, headers=headers, params=params)

    # Group the ncn nodes by their racks
    rack_info(hsm_response,sls_response)

if __name__ == "__main__":
    main()
