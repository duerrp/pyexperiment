# Getting started

After installing vagrant on your system, you can get up and running
with a reproducible environment for pyexperiment with the following
commands:

```
git clone https://github.com/duerrp/pyexperiment.git
cd pyexperiment/vagrant
vagrant up
```

If you have never done this before, the `vagrant up` command will
download an image with a pre-configured Ubuntu14.04 and install all
dependencies for pyexperiment. You can then login by typing `vagrant
ssh` and start running the tests by typing:

```
cd pyexperiment
./run_tests
```
