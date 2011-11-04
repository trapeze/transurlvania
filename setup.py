#!/usr/bin/env python

import os
from setuptools import setup, find_packages

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='transurlvania',
    version='0.2.4',
    author='Sam Bull',
    author_email='sam@pocketuniverse.ca',
    url='https://github.com/trapeze/transurlvania',
    description="This application provides a collection of URL-related utilities for multi-lingual projects.",
    long_description=readme,
    packages=find_packages(exclude=['tests', 'tests.garfield']),
    classifiers=[
        'Framework :: Django',
        #'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'Django>=1.0',
    ],
    include_package_data=True,
)
