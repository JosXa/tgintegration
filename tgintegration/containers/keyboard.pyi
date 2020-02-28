import itertools
import re
import weakref
from typing import *

from pyrogram import Filters, KeyboardButton, Message
from pyrogram import InlineKeyboardButton
from pyrogram.api.types.messages import BotCallbackAnswer

from tgintegration import AwaitableAction
from tgintegration.interactionclient import InteractionClient


class ReplyKeyboard:
    _client: InteractionClient
    _peer_id: Union[int, str]
    _message_id: int
    rows: List[List[KeyboardButton]]

    def __init__(
        self,
        client: InteractionClient,
        chat_id: Union[int, str],
        message_id: int,
        button_rows: List[List[KeyboardButton]],
    ):
        pass

    def find_button(self, pattern) -> Optional[KeyboardButton]:
        pass

    def press_button(self, pattern, quote=False) -> Message:
        pass

    def press_button_await(
        self, pattern, filters=None, num_expected=None, raise_=True, quote=False
    ) -> "Response":
        pass

    @property
    def num_buttons(self) -> int:
        pass


class InlineKeyboard:
    def __init__(
        self,
        client: InteractionClient,
        chat_id: Union[int, str],
        message_id: int,
        button_rows: List[List[InlineKeyboardButton]],
    ):
        pass

    def find_button(
        self, pattern: Optional[Pattern] = None, index: Optional[int] = None
    ) -> Optional[InlineKeyboardButton]:
                pass

    def press_button(
        self, pattern: Optional[Pattern] = None, index: Optional[int] = None
    ) -> BotCallbackAnswer:
        pass

    def press_button_await(
        self,
        pattern: Union[Pattern, str] = None,
        index: Optional[int] = None,
        num_expected: Optional[int] = None,
        max_wait: float = 8,
        min_wait_consecutive: float = 1.5,
        raise_: Optional[bool] = True,
    ):
        pass

    def __eq__(self, other):
        pass

    @property
    def num_buttons(self):
        pass


class NoButtonFound(Exception):
    pass
