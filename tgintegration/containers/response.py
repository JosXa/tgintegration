import time
from datetime import datetime
from typing import *
from typing import Any, List, Set, TypeVar

from pyrogram import InlineKeyboardMarkup, ReplyKeyboardMarkup, Client
from pyrogram import Message

from tgintegration.awaitableaction import AwaitableAction
from tgintegration.containers.keyboard import ReplyKeyboard, InlineKeyboard


class Response:
    def __init__(self, client: Client, to_action: AwaitableAction):
        self._client = client
        self.action = to_action

        self.started: Optional[float] = None
        self.action_result: Any = None
        self._messages: List[Message] = []

        # cached properties
        self.__reply_keyboard: Optional[ReplyKeyboard] = None
        self.__inline_keyboards: List[InlineKeyboard] = []

    @property
    def messages(self) -> List[Message]:
        return self._messages

    def _add_message(self, message: Message):
        message.exact_timestamp = time.time()
        self._messages.append(message)

    @property
    def empty(self) -> bool:
        return not self._messages

    @property
    def num_messages(self) -> int:
        return len(self._messages)

    @property
    def full_text(self) -> str:
        return "\n".join(x.text for x in self._messages if x.text) or ""

    @property
    def reply_keyboard(self) -> Optional[ReplyKeyboard]:
        if self.__reply_keyboard:
            return self.__reply_keyboard
        if self.empty:
            return None

        # Contingent upon the way Telegram works,
        # only the *last* message with buttons in a response object matters
        messages = reversed(self.messages)
        for m in messages:
            if isinstance(m.reply_markup, ReplyKeyboardMarkup):
                last_kb_msg = m
                break
        else:
            return None  # No message with a keyboard found

        reply_keyboard = ReplyKeyboard(
            client=self._client,
            chat_id=last_kb_msg.chat.id,
            message_id=last_kb_msg.message_id,
            button_rows=last_kb_msg.reply_markup.keyboard,
        )
        self.__reply_keyboard = reply_keyboard
        return reply_keyboard

    @property
    def inline_keyboards(self) -> Optional[List[InlineKeyboard]]:
        if self.__inline_keyboards:
            return self.__inline_keyboards
        if self.empty:
            return None

        inline_keyboards = []

        for message in self.messages:
            if isinstance(message.reply_markup, InlineKeyboardMarkup):
                inline_keyboards.append(
                    InlineKeyboard(
                        client=self._client,
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        button_rows=message.reply_markup.inline_keyboard,
                    )
                )

        self.__inline_keyboards = inline_keyboards
        return inline_keyboards

    @property
    def keyboard_buttons(self) -> Set[str]:
        all_buttons = set()
        for m in self._messages:
            markup = m.reply_markup
            if markup and hasattr(markup, "keyboard"):
                for row in markup.keyboard:
                    for button in row:
                        all_buttons.add(button)
        return all_buttons

    @property
    def last_message_timestamp(self) -> Optional[datetime]:
        if self.empty:
            return None
        # TODO: Dan should fix this
        return datetime.fromtimestamp(self._messages[-1].date)

    @property
    def commands(self) -> Set[str]:
        all_commands = set()
        for m in self._messages:
            entity_commands = [x for x in m.entities if x.type == "bot_command"]
            for e in entity_commands:
                all_commands.add(m.text[e.offset, len(m.text) - e.length])
            caption_entity_commands = [x for x in m.entities if x.type == "bot_command"]
            for e in caption_entity_commands:
                all_commands.add(m.caption[e.offset, len(m.caption) - e.length])
        return all_commands

    async def delete_all_messages(self, revoke: bool = True):
        peer_id = self._messages[0].chat.id
        await self._client.delete_messages(peer_id, [x.message_id for x in self._messages], revoke=revoke)

    def __eq__(self, other):
        if not isinstance(other, Response):
            return False

        return (
            self.full_text == other.full_text
            and self.inline_keyboards == other.inline_keyboards
            # TODO: self.keyboard == other.keyboard
        )

    def __getitem__(self, item):
        return self._messages[item]

    def __str__(self):
        if self.empty:
            return "Empty response"
        return "\nthen\n".join(['"{}"'.format(m.text) for m in self._messages])


class InvalidResponseError(Exception):
    pass
