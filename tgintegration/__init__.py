# -*- coding: utf-8 -*-

"""Top-level package for telegram-integration-test."""

__author__ = """Joscha Götzer"""
__email__ = 'joscha.goetzer@gmail.com'
__version__ = '0.1.0'

from tgintegration.interactionclient import AwaitableAction, Response, InteractionClient
from tgintegration.integrationtestclient import IntegrationTestClient

__all__ = [
    "AwaitableAction", "Response", "InteractionClient", "IntegrationTestClient"
]

