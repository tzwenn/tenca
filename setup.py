#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(
	name='tenca',
	version='0.0.1',
	packages=find_packages(),
	zip_safe=False,
	install_requires=[
		'mailmanclient',
	],
)
