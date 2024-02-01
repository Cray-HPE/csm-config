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

s3_user=ISCSI-SBPS
s3_bucket=boot-images
s3fs_mount_dir=/var/lib/cps-local/boot-images
filename=.iscsi-sbps.s3fs
passwd_file="${HOME}/${filename}"

radosgw-admin user info --uid "${s3_user}" |jq -r '.keys[]|.access_key +":"+ .secret_key' > "${passwd_file}"
chmod 600 "${passwd_file}"

mkdir -pv "${s3fs_mount_dir}"
s3fs "${s3_bucket}" "${s3fs_mount_dir}" -o "passwd_file=${passwd_file},url=http://rgw-vip.nmn,use_path_request_style"
