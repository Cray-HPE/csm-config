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

kubectl apply -f $1 
if [ $? -ne 0 ]; 
then
  echo "Unable to apply kyverno topology policy"
  exit 1
fi

deployments_to_restart=("cray-dns-powerdns" "cray-hbtd" "cray-hmnfd")
for service in "${deployments_to_restart[@]}"
do
  kubectl rollout restart deployment $service -n services
done

statefulsets_to_restart=("cray-keycloak" "cray-sls-postgres")
for service in "${statefulsets_to_restart[@]}"
do
  kubectl rollout restart statefulset $service -n services
done

kubectl rollout restart statefulset cray-spire-server -n spire
