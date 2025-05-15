#!/bin/bash
#
# MIT License
#
# (C) Copyright 2025 Hewlett Packard Enterprise Development LP
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

if ! kubectl apply -f $1
then
  echo "Unable to apply kyverno topology policy"
  exit 1
fi

deployments_to_restart=("cray-hmnfd" "cray-hbtd" "hpe-slingshot-jackaloped" "hpe-slingshot-ogopogod" "slingshot-fabric-manager"
                        "cray-dns-powerdns" "cray-powerdns-manager" "cray-dns-powerdns-manager" "cray-dhcp-kea" "cray-sls"
                        "cray-smd" "cray-bss" "cray-tftp" "cray-ipxe-aarch64" "cray-ipxe-x86-64" "cray-sts" "cfs-ara"
                        "cfs-hwsync-agent" "cfs-trust" "cray-cfs-api" "cray-cfs-api-db" "cray-cfs-batcher" "cray-cfs-operator"
                        "cray-bos" "cray-bos-db" "gitea-vcs" "cray-bss" "cray-sls" "cray-power-control" "cray-capmc"
                        "cray-tftp" "gitea-vcs")
for service in "${deployments_to_restart[@]}"
do
  kubectl rollout restart deployment $service -n services
  if [ $? -ne 0 ];
  then
    echo "Unable to restart deployment $service in services namespace"
  fi
done

deployments_to_restart=("coredns" "sealed-secrets" "cilium-operator")
for service in "${deployments_to_restart[@]}"
do
  kubectl rollout restart deployment $service -n kube-system
  if [ $? -ne 0 ];
  then
    echo "Unable to restart deployment $service in kube-system namespace"
  fi
done

deployments_to_restart=("istio-ingressgateway" "istio-ingressgateway-customer-admin" "istio-ingressgateway-customer-user"
                        "istio-ingressgateway-hmn" "istiod" "kiali")
for service in "${deployments_to_restart[@]}"
do
  kubectl rollout restart deployment $service -n istio-system
  if [ $? -ne 0 ];
  then
    echo "Unable to restart deployment $service in istio-system namespace"
  fi
done

deployments_to_restart=("cray-certmanager-cert-manager" "cray-certmanager-cert-manager-cainjector" "cray-certmanager-cert-manager-webhook")
for service in "${deployments_to_restart[@]}"
do
  kubectl rollout restart deployment $service -n cert-manager
  if [ $? -ne 0 ];
  then
    echo "Unable to restart deployment $service in cert-manager namespace"
  fi
done

deployments_to_restart=("kyverno-admission-controller" "kyverno-background-controller" "kyverno-cleanup-controller" "kyverno-reports-controller")
for service in "${deployments_to_restart[@]}"
do
  kubectl rollout restart deployment $service -n kyverno
  if [ $? -ne 0 ];
  then
    echo "Unable to restart deployment $service in kyverno namespace"
  fi
done

deployments_to_restart=("slurmctld" "slurmctld-backup" "slurmdbd" "slurmdbd-backup" "pbs" "pbs-comm")
for service in "${deployments_to_restart[@]}"
do
  kubectl rollout restart deployment $service -n user
  if [ $? -ne 0 ];
  then
    echo "Unable to restart deployment $service in user namespace"
  fi
done

deployments_to_restart=("cray-vault-configurer"  "cray-vault-operator")
for service in "${deployments_to_restart[@]}"
do
  kubectl rollout restart deployment $service -n vault
  if [ $? -ne 0 ];
  then
    echo "Unable to restart deployment $service in vault namespace"
  fi
done

kubectl rollout restart deploymet cray-ceph-csi-cephfs-provisioner -n ceph-cephfs
kubectl rollout restart deploymet cray-ceph-csi-rbd-provisioner -n ceph-rbd
kubectl rollout restart deployment cray-activemq-artemis-operator-controller-manager -n dvs
kubectl rollout restart deployment slurm-operator -n slurm-operator
kubectl rollout restart deployment istio-operator -n istio-operator
kubectl rollout restart deployment nexus -n nexus

statefulsets_to_restart=("cray-hmnfd-bitnami-etcd" "cray-hbtd-bitnami-etcd" "hpe-slingshot-vnid" "cray-console-node" 
                         "cray-keycloak" "cray-bss-bitnami-etcd" "cray-power-control-bitnami-etcd")
for service in "${statefulsets_to_restart[@]}"
do
  kubectl rollout restart statefulset $service -n services
  if [ $? -ne 0 ];
  then
    echo "Unable to restart StatefulSet $service in services namespace"
  fi
done

statefulsets_to_restart=("cray-spire-server"  "spire-server")
for service in "${statefulsets_to_restart[@]}"
do
  kubectl rollout restart statefulset $service -n spire
  if [ $? -ne 0 ];
  then
    echo "Unable to restart StatefulSet $service in spire namespace"
  fi
done

kubectl rollout restart statefulset cray-vault -n vault
kubectl rollout restart statefulset cray-dvs-mqtt-ss -n dvs

