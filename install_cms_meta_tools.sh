#!/bin/bash

# Copyright 2020-2021 Hewlett Packard Enterprise Development LP
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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# (MIT License)

CMT_RPMS_URL=http://car.dev.cray.com/artifactory/internal/SCMS/sle15_sp2/noarch/release/cmt-0.1/cms-team/

# Find latest cms-meta-tools RPM in our chosen release (0.1)
function cmt-rpm-url
{
    curl -s $CMT_RPMS_URL | 
        # Filter out everything except the RPM names
        grep -Eo "cms-meta-tools-[0-9][0-9]*[.][0-9][0-9]*[.][0-9][0-9]*-[0-9][0-9]*_[0-9a-f][0-9a-f]*[.]noarch[.]rpm" | 
        # Extract the version and build date and print those numbers followed by the full URL to the RPM
        sed "s#^cms-meta-tools-\([0-9][0-9]*\)[.]\([0-9][0-9]*\)[.]\([0-9][0-9]*\)-\([0-9][0-9]*\)_.*\$#\1 \2 \3 \4 $CMT_RPMS_URL\0#" |
        # Sort numerically by those fields, higher numbers first 
        sort -u -n -r -t" " -k1 -k2 -k3 -k4 | 
        # Take the first one and print only the RPM URL
        head -1 | awk -F" " '{ print $NF }'
}

RPM_URL=$(cmt-rpm-url)
if [ -n "$RPM_URL" ]; then
    echo "cms-meta-tools RPM: $RPM_URL"
else
    echo "Unable to find latest cms-meta-tools RPM in $CMT_RPMS_URL" 1>&2
    exit 1
fi

TRGDIR=$(pwd)/cms_meta_tools
mkdir -pv "$TRGDIR" || exit 1

# Install the rpm into this directory, do not check/update the rpm db, and (because of that) do not check dependencies
rpm -Uvh --relocate /opt/cray/cms-meta-tools="$TRGDIR" --nodeps --dbpath "$TRGDIR" $RPM_URL || exit 1
exit 0
