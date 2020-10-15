# -*- coding: utf-8 -*-
"""
The root package of `tgintegration`.
"""
from tgintegration.awaitableaction import AwaitableAction
from tgintegration.botcontroller import BotController
from tgintegration.containers.inlineresults import InlineResult
from tgintegration.containers.inlineresults import InlineResultContainer
from tgintegration.containers.keyboard import InlineKeyboard
from tgintegration.containers.keyboard import ReplyKeyboard
from tgintegration.containers.response import InvalidResponseError
from tgintegration.containers.response import Response
from tgintegration.interactionclient import InteractionClient


__author__ = """Joscha Götzer"""
__email__ = "joscha.goetzer@gmail.com"
__version__ = "0.4.0"

__all__ = [
    "AwaitableAction",
    "Response",
    "BotController",
    "InlineResult",
    "InlineResultContainer",
    "InvalidResponseError",
    "InlineKeyboard",
    "ReplyKeyboard",
    "InteractionClient",
]
