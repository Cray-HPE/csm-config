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

FROM artifactory.algol60.net/registry.suse.com/suse/sle15:15.3 as product-content-base
ARG SLES_MIRROR=https://slemaster.us.cray.com/SUSE
ARG ARCH=x86_64
RUN \
  zypper --non-interactive rr --all &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Basesystem/15-SP3/${ARCH}/product/ sles15sp3-Module-Basesystem-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Basesystem/15-SP3/${ARCH}/update/ sles15sp3-Module-Basesystem-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Development-Tools/15-SP3/${ARCH}/product/ sles15sp3-Module-Development-Tools-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Development-Tools/15-SP3/${ARCH}/update/ sles15sp3-Module-Development-Tools-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Containers/15-SP3/${ARCH}/product/ sles15sp3-Module-Containers-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Containers/15-SP3/${ARCH}/update/ sles15sp3-Module-Containers-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Desktop-Applications/15-SP3/${ARCH}/product/ sles15sp3-Module-Desktop-Applications-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Desktop-Applications/15-SP3/${ARCH}/update/ sles15sp3-Module-Desktop-Applications-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-HPC/15-SP3/${ARCH}/product/ sles15sp3-Module-HPC-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-HPC/15-SP3/${ARCH}/update/ sles15sp3-Module-HPC-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Legacy/15-SP3/${ARCH}/product/ sles15sp3-Module-Legacy-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Legacy/15-SP3/${ARCH}/update/ sles15sp3-Module-Legacy-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Public-Cloud/15-SP3/${ARCH}/product/ sles15sp3-Module-Public-Cloud-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Public-Cloud/15-SP3/${ARCH}/update/ sles15sp3-Module-Public-Cloud-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Python2/15-SP3/${ARCH}/product/ sles15sp3-Module-Python2-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Python2/15-SP3/${ARCH}/update/ sles15sp3-Module-Python2-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Server-Applications/15-SP3/${ARCH}/product/ sles15sp3-Module-Server-Applications-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Server-Applications/15-SP3/${ARCH}/update/ sles15sp3-Module-Server-Applications-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Web-Scripting/15-SP3/${ARCH}/product/ sles15sp3-Module-Web-Scripting-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Web-Scripting/15-SP3/${ARCH}/update/ sles15sp3-Module-Web-Scripting-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Product-SLES/15-SP3/${ARCH}/product/ sles15sp3-Product-SLES-product &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Product-SLES/15-SP3/${ARCH}/update/ sles15sp3-Product-SLES-update &&\
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-INSTALLER/15-SP3/${ARCH}/update/ sles15sp3-SLE-INSTALLER-update &&\
  zypper --non-interactive clean &&\
  zypper --non-interactive --gpg-auto-import-keys refresh

# Install dependencies as RPMs
RUN zypper ar --no-gpgcheck https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/ csm && \
    zypper refresh && \
    zypper in -y \
        csm-ssh-keys-roles

# Use for testing/not in pipeline builds
FROM artifactory.algol60.net/csm-docker/stable/cf-gitea-import:@CF_GITEA_IMPORT_VERSION@

WORKDIR /
ENV CF_IMPORT_PRODUCT_NAME=csm
ADD .version /product_version

# Copy in dependencies' Ansible content
COPY --from=product-content-base /opt/cray/ansible/roles/      /content/roles/

# Copy in CSM Ansible content
COPY ansible/ /content/

# Base image entrypoint takes it from here

