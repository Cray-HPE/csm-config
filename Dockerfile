# Dockerfile for importing CSM content into gitea, to be used with CFS
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

FROM arti.dev.cray.com/baseos-docker-master-local/sles15sp2:sles15sp2 as product-content-base
WORKDIR /

# Install dependencies as RPMs
RUN zypper ar --no-gpgcheck http://car.dev.cray.com/artifactory/csm/SCMS/sle15_sp2_ncn/x86_64/release/csm-1.1 csm-1.1 && \
    zypper refresh && \
    zypper in -y \
        csm-ssh-keys-roles

# Use the cf-gitea-import as a base image with CSM content copied in
FROM artifactory.algol60.net/csm-docker/stable/cf-gitea-import:@cf_gitea_import_image_tag@

# Use for testing/not in pipeline builds
#FROM arti.dev.cray.com/csm-docker-unstable-local/cf-gitea-import:latest

WORKDIR /
ENV CF_IMPORT_PRODUCT_NAME=csm
ADD .version /product_version

# Copy in dependencies' Ansible content
COPY --from=product-content-base /opt/cray/ansible/roles/      /content/roles/

# Copy in CSM Ansible content
COPY ansible/ /content/

# Base image entrypoint takes it from here

