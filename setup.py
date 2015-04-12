"""Setup for pyexperiment
"""
from __future__ import print_function
# from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a
# top level
# README file and 2) it's easier to type in the README file than to
# put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pyexperiment",
    version="0.1.9",
    author="Peter Duerr",
    author_email="duerrp@gmail.com",
    description="Framework for easy and clean experiments with python.",
    license="MIT",
    keywords="science experiment",
    url="https://github.com/duerrp/pyexperiment",
    download_url="https://github.com/duerrp/pyexperiment/tarball/0.1.9",
    packages=['pyexperiment',
              'pyexperiment.conf',
              'pyexperiment.state',
              'pyexperiment.utils',
              'pyexperiment.log',
          ],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
