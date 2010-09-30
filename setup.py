#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="redsolutioncms",
    version="0.0.1",
    description=("Django ditributed site management system"),
    license="LGPL",
    keywords="django CMS",

    author="Alexander Ivanov, Ivan Gromov",
    author_email="src@redsolution.ru",

    maintainer='Ivan Gromov',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
    ],
    packages=find_packages(),
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
#    long_description=open('README').read(),
    entry_points = {
        'console_scripts': ['redsolutioncms=redsolutioncms.loader:main'],
    },
)