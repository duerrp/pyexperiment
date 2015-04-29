#!/usr/bin/env sh

sudo apt-get update
sudo apt-get install -y \
     libhdf5-dev \
     pkg-config \
     libfreetype6-dev \
     libpng12-dev \
     python-dev \
     python-pip

sudo pip install Cython
sudo pip install -r /home/vagrant/pyexperiment/docker/requirements.txt

echo "export PYTHONPATH='.'" >> /home/vagrant/.bashrc
