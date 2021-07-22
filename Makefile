# Copyright 2021 Hewlett Packard Enterprise Development LP
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

# Docker Image
NAME ?= csm-config
VERSION := @DOCKER_VERSION@

# Helm Chart
CHART_PATH ?= kubernetes
CHART_NAME ?= csm-config
CHART_VERSION := @CHART_VERSION@
HELM_UNITTEST_IMAGE ?= quintush/helm-unittest:3.3.0-0.2.5

all: lint image chart_setup chart_package
chart: chart_setup chart_package chart_test

image: 
	docker build --pull ${DOCKER_ARGS} --tag '${NAME}:${VERSION}' .

lint:
	./runLint.sh

chart_package:
	cat ${CHART_PATH}/${NAME}/values.yaml
	helm dep up ${CHART_PATH}/${CHART_NAME}
	helm package ${CHART_PATH}/${CHART_NAME} -d ${CHART_PATH}/.packaged --version ${CHART_VERSION}

chart_setup:
	mkdir -p ${CHART_PATH}/.packaged

chart_test:
	helm lint "${CHART_PATH}/${NAME}"
	docker run --rm -v ${PWD}/${CHART_PATH}:/apps ${HELM_UNITTEST_IMAGE} -3 ${NAME}

