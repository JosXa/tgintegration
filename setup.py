#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from pip._internal.req import parse_requirements
from setuptools import setup, find_packages

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

setup(
    name='tgintegration',
    version='0.1.4',
    description="An Integration Test Library for Telegram Messenger Bots on top of Pyrogram.",
    long_description=readme + '\n\n' + history,
    author="Joscha Götzer",
    author_email='joscha.goetzer@gmail.com',
    url='https://github.com/JosXa/tgintegration',
    packages=find_packages(include=['tgintegration', 'tgintegration.containers']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords=['test', 'telegram', 'integration', 'bot', 'automation'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
