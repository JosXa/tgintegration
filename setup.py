#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pyrogram'
]

setup_requirements = [
    'pytest-runner',
    # TODO(JosXa): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='telegram-integration-test',
    version='0.1.1',
    description="An Integration Test Library for Telegram Messenger Bots on top of Pyrogram.",
    long_description=readme + '\n\n' + history,
    author="Joscha Götzer",
    author_email='joscha.goetzer@gmail.com',
    url='https://github.com/JosXa/telegram-integration-test',
    packages=find_packages(include=['tgintegration']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords=['test', 'telegram', 'integration', 'bot', 'continuous'],
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
