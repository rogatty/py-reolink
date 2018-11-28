# coding=utf-8
"""PyReolink setup script."""
from setuptools import setup

setup(
    name='pyreolink',
    packages=['pyreolink'],
    version='0.0.1',
    description='Python Reolink is a library written in Python 3x ' +
                'that exposes the Reolink cameras as Python objects.',
    author='Igor Rogatty',
    author_email='igor.rogatty@gmail.com',
    url='https://github.com/rogatty/pyreolink',
    license='LGPLv3+',
    include_package_data=True,
    install_requires=['requests']
)
