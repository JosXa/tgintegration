from datetime import datetime
from typing import Any, List, Pattern, Set

from pyrogram import Message

from tgintegration import InteractionClient
from tgintegration.awaitableaction import AwaitableAction
from tgintegration.containers import InlineKeyboard, ReplyKeyboard


class Response:
    client: InteractionClient
    action: AwaitableAction

    started: float
    action_result: Any
    _messages: List[Message]
    empty: bool
    full_text: str
    reply_keyboard: ReplyKeyboard
    inline_keyboards: List[InlineKeyboard]
    keyboard_buttons: Set[str]
    last_message_timestamp: datetime

    messages: List[Message]

    __reply_keyboard: ReplyKeyboard
    __inline_keyboards: List[InlineKeyboard]

    def __init__(self, client: InteractionClient, to_action: AwaitableAction):
        ...

    def _add_message(self, message: Message):
        ...

    def press_inline_button(self, pattern: Pattern):
        ...

    def __getitem__(self, item):
        ...

    def __str__(self):
        ...


class InvalidResponseError(Exception): ...
