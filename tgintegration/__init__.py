# -*- coding: utf-8 -*-
"""
The root module of `tgintegration` {{tgi}}.
"""
from tgintegration.botcontroller import BotController
from tgintegration.containers import InlineKeyboard
from tgintegration.containers import InlineResult
from tgintegration.containers import InlineResultContainer
from tgintegration.containers import InvalidResponseError
from tgintegration.containers import ReplyKeyboard
from tgintegration.containers import Response


__author__ = """Joscha Götzer"""
__email__ = "joscha.goetzer@gmail.com"
__version__ = "0.4.0"

__all__ = [
    "Response",
    "BotController",
    "InlineResult",
    "InlineResultContainer",
    "InvalidResponseError",
    "InlineKeyboard",
    "ReplyKeyboard",
]
