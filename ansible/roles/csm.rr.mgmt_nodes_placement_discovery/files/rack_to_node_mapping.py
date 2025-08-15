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

import base64
from collections import defaultdict
import json
import re
import subprocess
import sys
from typing import Union

import requests

# Define the endpoint URL
hsm_url = "https://api-gw-service-nmn.local/apis/smd/hsm/v2/State/Components"
sls_url= "https://api-gw-service-nmn.local/apis/sls/v1/search/hardware"

# A partial regular expression for xnames (up through the 'c' character)
# It has a capture group defined to get the first 5 characters
xname_regex = re.compile(r'^(x[0-9]{4})c')

# Building blocks for NCN name regular expression
# These numeric blocks are defined because the NCN number must have a non-0 digit in it.

# First number is non-0
ncn_num_1 = r'[1-9][0-9]{2}'
# Second number is non-0
ncn_num_2 = r'0[1-9][0-9]'
# Third number is non-0
ncn_num_3 = r'00[1-9]'

# A regular expression for management NCN aliases that are found in SLS
# Non-capturing group defined, because if it matches, we want the entire string anyway
# This is split up across multiple lines for improved human readability
ncn_regex = re.compile(
    r'^ncn-[msw]' + r'(?:' + \
        ncn_num_1 + r'|' + ncn_num_2 + r'|' + ncn_num_3 + \
    r')$'
)

def print_stderr(msg: str) -> None:
    """
    Prints the specified message to stderr (with a newline appended),
    and then flushes stderr.
    """
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()

# Get the authentication token
def token_fetch(client_secret: str) -> Union[str, None]:
    """
    Fetch the keycloak token.
    Return keycloak token.
    """
    response = None

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

def rack_info(hsm_data: dict, sls_data: dict) -> None:
    """
    Get/ extract  management racks and corresponding management nodes (master, worker and storage)
    from HSM and SLS.
    hsm_data: Decoded response body from GET request to HSM endpoint
    sls_data: Decoded response body from GET request to SLS endpoint
    Group and write rack to management nodes mapping into to file /tmp/rack_info.txt, to be consumed
    by zoning functions (k8s and ceph).
    Returns nothing.
    """

    component_ids = [
        component['ID'] for component in hsm_data["Components"]
        if component.get("Role") == "Management" and component.get("SubRole") in {"Master", "Worker", "Storage"}
    ]

    # Group by rack ID (extracted from "ID")
    res_rack = defaultdict(list)

    for xname in component_ids:
        match = xname_regex.match(xname)
        if match is None:
            print_stderr(f"Component xname in HSM response has invalid format: {xname}")
            sys.exit(1)
        rack_id = match.group(1) # Extract "x3000" from "x3000c0s1b75n75"
        # Set a sentinel to indicate that we have found the alias for this xname in SLS
        found_alias = False
        for sls_entry in sls_data:
            if sls_entry["Xname"] != xname:
                continue
            for alias in sls_entry["ExtraProperties"]["Aliases"]:
                if ncn_regex.match(alias) is None:
                    continue
                # That means this alias is of the form ncn-[msw]###,
                # which is what we're looking for
                res_rack[rack_id].append(alias)
                found_alias=True
                break
            if found_alias:
                break
        if not found_alias:
            print_stderr(f"Component {xname} has no alias in SLS of the form ncn-[msw]###")
            sys.exit(1)

    res_rack_str = json.dumps(res_rack, indent=4)
    print(res_rack)
    # Write the result to the tmp file
    with open("/tmp/rack_info.txt", "w") as file:
        file.write(res_rack + "\n")

def main() -> None:
    """
    Discover/ fetch/ group management racks and corresponding mapped management nodes
    info (xnames in the form of key value pair) from HSM and SLS and store it under
    /tmp/rack_info.txt file to be consumed by zoning(k8s and ceph) functions.
    """
    if len(sys.argv) != 2:
       print_stderr("Usage: python3 rack_to_node_mapping.py <client_secret> ")
       sys.exit(1)

    # Fetch the keycloak token
    client_secret = sys.argv[1]
    token = token_fetch(client_secret)
    if token is None:
        print_stderr("Failed to get the keycloak token")
        sys.exit(1)

    # Parameters for sls
    params = {"type": "comptype_node"}
    headers = {
        "Authorization": f"Bearer {token}",  # Add the token as a Bearer token
        "Accept": "application/json"         # Indicate you want a JSON response
    }

    # Make the GET request to hsm enpoint
    with requests.get(hsm_url, headers=headers) as hsm_response:
        # Check the response status
        if hsm_response.status_code != 200:
            print_stderr(f"HSM request failed. Status code: {hsm_response.status_code}")
            print_stderr(f"Response text: {hsm_response.text}")
            sys.exit(1)

        # Decode the response body
        hsm_data = hsm_response.json()

    # Make the GET request to sls enpoint
    with requests.get(sls_url, headers=headers, params=params) as sls_response:
        # Check the response status
        if sls_response.status_code != 200:
            print_stderr(f"SLS request failed. Status code: {sls_response.status_code}")
            print_stderr(f"Response text: {sls_response.text}")
            sys.exit(1)

        # Decode the response body
        sls_data = sls_response.json()

    # Group the ncn nodes by their racks
    rack_info(hsm_data, sls_data)

if __name__ == "__main__":
    main()
