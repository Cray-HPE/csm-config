#!/bin/bash
#
# MIT License
#
# (C) Copyright 2024 Hewlett Packard Enterprise Development LP
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

set -euo pipefail

# Get Host Name, HSN IP and NMN IP of worker node
host_name="$(awk '{print $1}' /etc/hostname)"

hsn_ip="$(ip addr | grep "hsn0$" | awk '{print $2;}')" || true

if [[ -n $hsn_ip ]]
then
  hsn_ip="$(echo $hsn_ip | awk -F\/ '{print $1;}')"
fi

nmn_ip="$(ip addr | grep "nmn0$" | awk '{print $2;}' | awk -F\/ '{print $1;}')"

# echo the details to stdout to be picked by next task in the playbook
echo "$host_name:$hsn_ip:$nmn_ip"
