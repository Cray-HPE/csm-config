# Dockerfile for importing CSM content into gitea, to be used with CFS
# Copyright 2020 Hewlett Packard Enterprise Development LP

FROM dtr.dev.cray.com/baseos/sles15sp1 as product-content-base
WORKDIR /

# Install dependencies as RPMs
RUN zypper ar --no-gpgcheck http://car.dev.cray.com/artifactory/csm/SCMS/sle15_sp1_ncn/x86_64/release/shasta-1.4/ csm && \
    zypper refresh && \
    zypper in -y \
        csm-ssh-keys-roles

# Use the cf-gitea-import as a base image with CSM content copied in
FROM dtr.dev.cray.com/cray/cf-gitea-import:@cf_gitea_import_image_tag@

# Use for testing/not in pipeline builds
#FROM dtr.dev.cray.com/cray/cf-gitea-import:latest 

WORKDIR /
ENV CF_IMPORT_PRODUCT_NAME=csm
ADD csm_product_version /product_version

# Copy in dependencies' Ansible content
COPY --from=product-content-base /opt/cray/ansible/roles/      /content/roles/
#COPY --from=product-content-base /opt/cray/ansible/playbooks/ /content/playbooks/

# Copy in CSM Ansible content
COPY ansible/ /content/

# Base image entrypoint takes it from here
