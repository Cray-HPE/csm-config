# (C) Copyright 2021 Hewlett Packard Enterprise Development LP
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

# If you wish to perform a local build, you will need to clone or copy the contents of the
# cms-meta-tools repo to ./cms_meta_tools

NAME ?= csm-config
DOCKER_VERSION ?= $(shell head -1 .docker_version)
CHART_VERSION ?= $(shell head -1 .chart_version)

# Helm Chart
CHART_PATH ?= kubernetes
CHART_NAME ?= $(NAME)

CONFIG_IMAGE_NAME ?= $(NAME)
CONFIG_IMAGE_TAG ?= $(CHART_VERSION)

HELM_UNITTEST_IMAGE ?= quintush/helm-unittest:3.3.0-0.2.5

all: runbuildprep lint image chart
chart: chart_setup chart_package chart_test

runbuildprep:
		# Set the docker image name for the config image
		echo "config_image_name=${CONFIG_IMAGE_NAME}"
		[ -n "${CONFIG_IMAGE_NAME}" ]
		sed -i s/@config_image_name@/${CONFIG_IMAGE_NAME}/g ${CHART_PATH}/${CHART_NAME}/values.yaml
		# Debug
		cat ${CHART_PATH}/${CHART_NAME}/values.yaml
		
		# Set the docker image tag for the config image

		echo "config_image_tag=${CONFIG_IMAGE_TAG}"
		[ -n "${CONFIG_IMAGE_TAG}" ]
		sed -i s/@config_image_tag@/${CONFIG_IMAGE_TAG}/g ${CHART_PATH}/${CHART_NAME}/values.yaml
		
		# Set the product name
		sed -i s/@product_name@/csm/g ${CHART_PATH}/${CHART_NAME}/values.yaml
		
		# runBuildPrep calls update_versions, which will 
		# replace @product_version@ string in Chart.yaml and values.yaml
		# We call a local copy of runBuildPrep because we need to do some
		# fancy footwork with the csm-ssh-keys version as well
		./runBuildPrep.sh
		
		# Debug
		cat Dockerfile
		cat ${CHART_PATH}/${CHART_NAME}/values.yaml

lint:
		./cms_meta_tools/scripts/runLint.sh

image:
		docker build --pull ${DOCKER_ARGS} --tag '${NAME}:${DOCKER_VERSION}' .

chart_setup:
		mkdir -p ${CHART_PATH}/.packaged
		printf "\nglobal:\n  appVersion: ${DOCKER_VERSION}" >> ${CHART_PATH}/${CHART_NAME}/values.yaml

chart_package:
		helm dep up ${CHART_PATH}/${CHART_NAME}
		helm package ${CHART_PATH}/${CHART_NAME} -d ${CHART_PATH}/.packaged --app-version ${DOCKER_VERSION} --version ${CHART_VERSION}

chart_test:
		helm lint "${CHART_PATH}/${CHART_NAME}"
		docker run --rm -v ${PWD}/${CHART_PATH}:/apps ${HELM_UNITTEST_IMAGE} -3 ${CHART_NAME}
