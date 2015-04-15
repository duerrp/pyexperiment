# Getting started

After installing docker on your system, you can get up and running
with a reproducible environment for pyexperiment by issuing the
following commands:

```
git clone https://github.com/duerrp/pyexperiment.git
cd pyexperiment/docker
./build.sh
```

If you have never done this before, the `./build.sh` command will
download an image with a pre-configured Ubuntu14.04 and install all
dependencies for pyexperiment. You can then start a bash prompt in the
image by typing `./run.sh` and start running the tests by typing:

```
cd ~/pyexperiment
./run_tests
```
