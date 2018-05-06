from typing import List, Pattern, Union

from pyrogram import InlineKeyboardButton, KeyboardButton
from pyrogram.api.types import Message
from pyrogram.api.types.messages import BotCallbackAnswer
from pyrogram.client.filters.filter import Filter
from tgintegration import InteractionClient, Response


class ReplyKeyboard:
    _client: InteractionClient
    _message_id: int
    _peer_id: int
    rows = List[List[KeyboardButton]]

    def __init__(
            self,
            client: InteractionClient,
            chat_id: int,
            message_id: int,
            button_rows: List[List[KeyboardButton]]
    ): ...

    def _find_button(self, pattern: Pattern) -> Union[KeyboardButton, None]:
        ...

    def press_button(self, pattern: Pattern, quote: bool = False) -> Message:
        ...

    def press_button_await(
            self,
            pattern: Pattern,
            filters: Filter = None,
            num_expected: int = None,
            raise_: bool = True,
            quote=False,
    ) -> Response:
        ...


class InlineKeyboard:
    _client: InteractionClient
    _message_id: int
    _peer_id: int
    rows: List[List[InlineKeyboardButton]]

    def __init__(
            self,
            client: InteractionClient,
            chat_id: int,
            message_id: int,
            button_rows: List[List[InlineKeyboardButton]]
    ):
        ...

    def _find_button(self, pattern: Pattern = None, index: int = None) -> Union[InlineKeyboardButton, None]:
        ...

    def press_button(self, pattern: Pattern = None, index: int = None) -> BotCallbackAnswer:
        ...

    def press_button_await(
            self,
            pattern: Pattern = None,
            index: int = None,
            num_expected: int = None,
            max_wait=8,
            min_wait_consecutive=1.5,
            raise_: bool = True,
    ) -> Response:
        ...


class NoButtonFound(Exception):
    pass
