#!/bin/bash

SCRIPT_DIR=$(dirname $0)

echo create inventory-nodejs deployment and service...
export CURRENTTIME=$( date '+%F_%H:%M:%S' )
echo CURRENTTIME is $CURRENTTIME  ...this will be appended to generated deployment yaml

cp inventory-nodejs-deployment.yaml inventory-nodejs-deployment-$CURRENTTIME.yaml

IMAGE_NAME=inventory-nodejs
IMAGE_VERSION=0.1

#may hit sed incompat issue with mac
sed -i "s|%DOCKER_REGISTRY%|${DOCKER_REGISTRY}|g" inventory-nodejs-deployment-$CURRENTTIME.yaml
sed -i "s|%INVENTORY_PDB_NAME%|${INVENTORY_PDB_NAME}|g" inventory-nodejs-deployment-$CURRENTTIME.yaml

export IMAGE=${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_VERSION}

if [ -z "$1" ]; then
    kubectl apply -f $SCRIPT_DIR/inventory-nodejs-deployment-$CURRENTTIME.yaml -n msdataworkshop
else
    kubectl apply -f <(istioctl kube-inject -f $SCRIPT_DIR/inventory-nodejs-deployment-$CURRENTTIME.yaml) -n msdataworkshop
fi

