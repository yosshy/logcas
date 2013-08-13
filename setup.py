#!/usr/bin/env python

from distutils.core import setup

setup(
    name='LogCAS',
    version='0.1',
    description='Log Collecting and Analyzing System for OpenStack',
    author='Akira Yoshiyama',
    author_email='akirayoshiyama@gmail.com',
    url='https://github.com/yosshy/logcas',
    packages=['logcas', 'logcas.logger'],
    package_dir={'logcas': 'logcas',
                 'logcas.logger': 'logcas/logger'},
    package_data={'logcas': ['static/*', 'templates/*']},
)
