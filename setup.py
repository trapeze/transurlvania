import os
from setuptools import setup, find_packages

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='transurlvania',
    version='0.2.0a', 
    description="A collection of URL-related utilities for multi-lingual projects",
    long_description=readme,
    author='sbull',
    url='https://github.com/trapeze/transurlvania',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires=[
        'Django>=1.0'
    ],
)
