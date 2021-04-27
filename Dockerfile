# Dockerfile for importing CSM content into gitea, to be used with CFS
# Copyright 2020-2021 Hewlett Packard Enterprise Development LP

FROM arti.dev.cray.com/baseos-docker-master-local/sles15sp1:sles15sp1 as product-content-base
WORKDIR /

# Install dependencies as RPMs
RUN zypper ar --no-gpgcheck http://car.dev.cray.com/artifactory/csm/SCMS/sle15_sp1_ncn/x86_64/dev/master/ csm && \
    zypper refresh && \
    zypper in -y \
        csm-ssh-keys-roles

# Use the cf-gitea-import as a base image with CSM content copied in
FROM arti.dev.cray.com/csm-docker-stable-local/cf-gitea-import:@cf_gitea_import_image_tag@

# Use for testing/not in pipeline builds
#FROM arti.dev.cray.com/csm-docker-stable-local/cf-gitea-import:latest

WORKDIR /
ENV CF_IMPORT_PRODUCT_NAME=csm
ADD .version /product_version

# Copy in dependencies' Ansible content
COPY --from=product-content-base /opt/cray/ansible/roles/      /content/roles/
#COPY --from=product-content-base /opt/cray/ansible/playbooks/ /content/playbooks/

# Copy in CSM Ansible content
COPY ansible/ /content/

# Base image entrypoint takes it from here
