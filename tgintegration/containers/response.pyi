import time
from datetime import datetime
from typing import *
from typing import Any, List, Set

from pyrogram import InlineKeyboardMarkup, ReplyKeyboardMarkup
from pyrogram import Message

from tgintegration.awaitableaction import AwaitableAction
from tgintegration.containers.keyboard import ReplyKeyboard, InlineKeyboard
from tgintegration.interactionclient import InteractionClient


class Response:
    client: InteractionClient
    to_action: AwaitableAction
    _message: List[Message]

    def __init__(self, client: InteractionClient, to_action: AwaitableAction):
        pass

    @property
    def messages(self) -> List[Message]:
        pass

    def _add_message(self, message: Message):
        pass

    @property
    def empty(self) -> bool:
        pass

    @property
    def num_messages(self) -> int:
        pass

    @property
    def full_text(self) -> str:
        pass

    @property
    def reply_keyboard(self) -> Optional[ReplyKeyboard]:
        pass

    @property
    def inline_keyboards(self) -> Optional[List[InlineKeyboard]]:
        pass

    @property
    def keyboard_buttons(self) -> Set[str]:
        pass

    @property
    def last_message_timestamp(self) -> Optional[datetime]:
        pass

    @property
    def commands(self) -> Set[str]:
        pass

    def __eq__(self, other):
        pass

    def __getitem__(self, item):
        pass

    def __str__(self):
        pass


class InvalidResponseError(Exception):
    pass
