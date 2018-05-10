# -*- coding: utf-8 -*-
from tgintegration.botintegrationclient import BotIntegrationClient
from tgintegration.interactionclient import InteractionClient
from tgintegration.response import Response
from tgintegration.awaitableaction import AwaitableAction
from tgintegration.containers import InlineResult, InlineResultContainer


__author__ = """Joscha Götzer"""
__email__ = 'joscha.goetzer@gmail.com'
__version__ = '0.2.0'

__all__ = [
    "AwaitableAction", "Response", "InteractionClient", "BotIntegrationClient", "InlineResult",
    "InlineResultContainer"
]
