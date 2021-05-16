#!/usr/bin/env sh
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

./install_cms_meta_tools.sh || exit 1

# Set the docker image name for the config image
config_image_name=${IMAGE_NAME}
echo "config_image_name=${config_image_name}"
sed -i s/@config_image_name@/${config_image_name}/g kubernetes/csm-config/values.yaml

# Set the docker image tag for the config image
config_image_tag=${IMAGE_TAG}
echo "config_image_tag=${config_image_tag}"
sed -i s/@config_image_tag@/${config_image_tag}/g kubernetes/csm-config/values.yaml

# Set the product name
sed -i s/@product_name@/csm/g kubernetes/csm-config/values.yaml

# Replace @product_version@ string in Chart.yaml and values.yaml
./cms_meta_tools/update_versions/update_versions.sh || exit 1
rm -rf ./cms_meta_tools

# Set the cf-gitea-import image version (for the config import)
wget http://car.dev.cray.com/artifactory/csm/SCMS/noos/noarch/release/shasta-1.4/cms-team/manifest.txt
cf_gitea_import_image_tag=$(cat manifest.txt | grep cf-gitea-import | sed s/.*://g | tr -d '[:space:]')
sed -i s/@cf_gitea_import_image_tag@/${cf_gitea_import_image_tag}/g Dockerfile
rm manifest.txt

# Debug
cat kubernetes/csm-config/values.yaml
