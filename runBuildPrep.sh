#!/usr/bin/env sh
# Copyright 2020 Hewlett Packard Enterprise Development LP

PRODUCT_VERSION=$(cat csm_product_version)

# Set the docker image name for the config image
config_image_name=${IMAGE_NAME}
echo "config_image_name=${config_image_name}"
sed -i s/@config_image_name@/${config_image_name}/g kubernetes/csm-config/values.yaml

# Set the docker image tag for the config image
config_image_tag=${IMAGE_TAG}
echo "config_image_tag=${config_image_tag}"
sed -i s/@config_image_tag@/${config_image_tag}/g kubernetes/csm-config/values.yaml

# Set the product name and version
sed -i s/@product_name@/csm/g kubernetes/csm-config/values.yaml
sed -i s/@product_version@/${PRODUCT_VERSION}/g kubernetes/csm-config/values.yaml

# Set the cf-gitea-import image version (for the config import)
wget http://car.dev.cray.com/artifactory/csm/SCMS/noos/noarch/release/shasta-1.4/cms-team/manifest.txt
cf_gitea_import_image_tag=$(cat manifest.txt | grep cf-gitea-import | sed s/.*://g | tr -d '[:space:]')
sed -i s/@cf_gitea_import_image_tag@/${cf_gitea_import_image_tag}/g Dockerfile
rm manifest.txt

# Debug
cat kubernetes/csm-config/values.yaml
