#!/usr/bin/env python

from distutils.core import setup

setup(name='LogDAS',
      version='0.1',
      description='Log Analyzer for OpenStack',
      author='Akira Yoshiyama',
      author_email='akirayoshiyama@gmail.com',
      url='https://github.com/yosshy/logdas',
      packages=['logdas', 'logdas.logging'],
      package_dir={'logdas': 'logdas',
                   'logdas.logging': 'logdas/logging'},
      package_data={'logdas': ['static/*', 'templates/*']},
     )
