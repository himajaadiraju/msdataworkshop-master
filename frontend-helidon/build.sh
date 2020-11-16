#!/bin/bash

SCRIPT_DIR=$(dirname $0)

IMAGE_NAME=frontend-helidon
IMAGE_VERSION=0.1

if [ -z "DOCKER_REGISTRY" ]; then
    echo "Error: DOCKER_REGISTRY env variable needs to be set!"
    exit 1
fi

export IMAGE=${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_VERSION}
# this is not ideal but makes it convenient to access Jaeger UI from app page...
cp src/main/resources/web/index.html-template src/main/resources/web/index.html
sed -i "s|%JAEGER_QUERY_ADDRESS%|${JAEGER_QUERY_ADDRESS}|g" src/main/resources/web/index.html

mvn install
mvn package docker:build

if [ $DOCKERBUILD_RETCODE -ne 0 ]; then
    exit 1
fi
docker push $IMAGE
if [  $? -eq 0 ]; then
    docker rmi ${IMAGE}
fi