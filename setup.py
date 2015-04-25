"""Setup for pyexperiment
"""
from __future__ import print_function
# from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from pyexperiment import __version__

import os
from setuptools import setup

read_plain = lambda fname: open(
    os.path.join(os.path.dirname(__file__), fname), 'r').read()
try:
    from pypandoc import convert
    read_md = lambda fname: convert(fname, 'rst')
except ImportError:
    print("Warning: pypandoc module not found")
    read_md = read_plain

LONG_DESCRIPTION = 'Framework for easy and clean experiments with python.'
if os.path.exists('README.rst'):
    print("README.rst found...")
    LONG_DESCRIPTION = read_plain('README.rst')
elif os.path.exists('README.md'):
    print("RADME.md found, converting to rst")
    LONG_DESCRIPTION = read_md('README.md')

setup(
    name="pyexperiment",
    version=__version__,
    author="Peter Duerr",
    author_email="duerrp@gmail.com",
    description="Run experiments with Python - quick and clean.",
    license="MIT",
    keywords="science experiment",
    url="https://github.com/duerrp/pyexperiment",
    packages=['pyexperiment',
              'pyexperiment.utils'],
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
