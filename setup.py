#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os

from pip._internal.req import parse_requirements
from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

parsed_requirements = parse_requirements('requirements.txt', session='hack')
requirements = [str(ir.req) for ir in parsed_requirements]

parsed_dev_requirements = parse_requirements('requirements_dev.txt', session='hack')
requirements_dev = [str(ir.req) for ir in parsed_dev_requirements]

setup_requirements = [
    'pytest-runner',
    # TODO(JosXa): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

packages = find_packages(exclude='tests')

stub_files = []
for p in packages:
    path = p.replace('.', '/')
    files_in_path = [os.path.join(path, x) for x in os.listdir(path) if x.endswith('.pyi')]
    if files_in_path:
        stub_files.append(
            (path, files_in_path)
        )

setup(
    name='tgintegration',
    version='0.2.2',
    description="An Integration Test Library for Telegram Messenger Bots on top of Pyrogram.",
    long_description=readme + '\n\n' + history,
    author="Joscha Götzer",
    author_email='joscha.goetzer@gmail.com',
    url='https://github.com/JosXa/tgintegration',
    packages=packages,
    data_files=stub_files,
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords=['test', 'telegram', 'integration', 'bot', 'automation'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
