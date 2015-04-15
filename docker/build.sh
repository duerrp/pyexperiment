#!/usr/bin/env bash

# Copy the requirements file from parent directory if necessary
cmp --silent ../requirements.txt ./requirements.txt || cp ../requirements.txt ./

# Replace values in the template
cat Dockerfile.template | \
    sed "s/USERID/$UID/g" | \
    sed "s/GROUPID/$(id -g)/g"| \
    sed "s/USERNAME/$USER/g" > ./Dockerfile

# Build docker image
docker build -t ubuntu14.04-pyexperiment .
