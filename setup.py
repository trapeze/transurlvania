#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='transurlvania',
    version='0.0.1',
    author='Sam Bull',
    author_email='sbull@trapeze.com',
    url='https://github.com/trapeze/transurlvania',
    description = 'This application provides a collection of URL-related utilities for multi-lingual projects.',
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
)