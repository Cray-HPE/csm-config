#
# MIT License
#
# (C) Copyright 2020-2024 Hewlett Packard Enterprise Development LP
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
# Dockerfile for importing CSM content into gitea, to be used with CFS

FROM artifactory.algol60.net/registry.suse.com/suse/sle15:15.4 as product-content-base
WORKDIR /

ARG SP=4
ARG ARCH=x86_64

# Pin the version of csm-ssh-keys being installed. The actual version is substituted by
# the runBuildPrep script at build time
ARG CSM_SSH_KEYS_VERSION=@RPM_VERSION@

# Do zypper operations using a wrapper script, to isolate the necessary artifactory authentication
COPY zypper-docker-build.sh /
# The above script calls the following script, so we need to copy it as well
COPY zypper-refresh-patch-clean.sh /
RUN --mount=type=secret,id=ARTIFACTORY_READONLY_USER --mount=type=secret,id=ARTIFACTORY_READONLY_TOKEN \
    ./zypper-docker-build.sh && \
    rm /zypper-docker-build.sh /zypper-refresh-patch-clean.sh

FROM artifactory.algol60.net/csm-docker/stable/cf-gitea-import:@CF_GITEA_IMPORT_VERSION@ as cf-gitea-import-base

# apply security patches to the cf-gitea-import base image
#  NOTE: do this here in case base image isn't being updated regularly
USER root:root
RUN apk update && \
    apk add --upgrade apk-tools &&  \
    apk -U upgrade && \
    rm -rf /var/cache/apk/*

USER nobody:nobody
WORKDIR /
ENV CF_IMPORT_PRODUCT_NAME=csm
ADD .version /product_version

# Copy in dependencies' Ansible content
COPY --chown=nobody:nobody --from=product-content-base /opt/cray/ansible/roles/      /content/roles/

# Copy in CSM Ansible content
COPY --chown=nobody:nobody ansible/ /content/

# Base image entrypoint takes it from here
