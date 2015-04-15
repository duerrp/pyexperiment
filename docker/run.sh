#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Run docker with shared X11 sockets and pyexperiment folder
docker run \
       -e DISPLAY \
       -v /tmp/.X11-unix:/tmp/.X11-unix \
       -v $HOME/.Xauthority:$HOME/.Xauthority \
       -v $DIR/../:/home/$USER/pyexperiment/ \
       --net=host \
       --rm \
       -t \
       -i \
       ubuntu14.04-pyexperiment
