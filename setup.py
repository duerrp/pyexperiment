"""Setup for pyexperiment
"""
from __future__ import print_function
# from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import os
from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda fname: convert(fname, 'rst')
except ImportError:
    print("Warning: pypandoc module not found")
    read_md = lambda fname: open(
        os.path.join(os.path.dirname(__file__), fname), 'r').read()

LONG_DESCRIPTION = 'Framework for easy and clean experiments with python.'
if os.path.exists('README.md'):
    LONG_DESCRIPTION = read_md('README.md')

setup(
    name="pyexperiment",
    version="0.1.16-test2",
    author="Peter Duerr",
    author_email="duerrp@gmail.com",
    description="Run experiments with Python - quick and clean.",
    license="MIT",
    keywords="science experiment",
    url="https://github.com/duerrp/pyexperiment",
    # download_url="https://github.com/duerrp/pyexperiment/tarball/0.1.15",
    packages=['pyexperiment',
              'pyexperiment.conf',
              'pyexperiment.state',
              'pyexperiment.utils',
              'pyexperiment.log',
              ],
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
