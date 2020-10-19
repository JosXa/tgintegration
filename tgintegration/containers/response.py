from datetime import datetime
from time import time
from typing import Any
from typing import List
from typing import Optional
from typing import Set
from typing import TYPE_CHECKING

from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types import Message
from pyrogram.types import ReplyKeyboardMarkup

if TYPE_CHECKING:
    from tgintegration.botcontroller import BotController
from tgintegration.containers.keyboard import InlineKeyboard, ReplyKeyboard
from tgintegration.update_recorder import MessageRecorder


class Response:
    def __init__(self, controller: "BotController", recorder: MessageRecorder):
        self._controller = controller
        self._recorder = recorder

        self.started: Optional[float] = None
        self.action_result: Any = None

        # cached properties
        self.__reply_keyboard: Optional[ReplyKeyboard] = None
        self.__inline_keyboards: List[InlineKeyboard] = []

    @property
    def messages(self) -> List[Message]:
        return self._recorder.messages

    @property
    def is_empty(self) -> bool:
        return not self.messages

    @property
    def num_messages(self) -> int:
        return len(self.messages)

    @property
    def full_text(self) -> str:
        return "\n".join(x.text for x in self.messages if x.text) or ""

    @property
    def reply_keyboard(self) -> Optional[ReplyKeyboard]:
        if self.__reply_keyboard:
            return self.__reply_keyboard
        if self.is_empty:
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
            controller=self._controller,
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
        if self.is_empty:
            return None

        inline_keyboards = [
            InlineKeyboard(
                controller=self._controller,
                chat_id=message.chat.id,
                message_id=message.message_id,
                button_rows=message.reply_markup.inline_keyboard,
            )
            for message in self.messages
            if isinstance(message.reply_markup, InlineKeyboardMarkup)
        ]

        self.__inline_keyboards = inline_keyboards
        return inline_keyboards

    @property
    def keyboard_buttons(self) -> Set[str]:
        all_buttons = set()
        for m in self.messages:
            markup = m.reply_markup
            if markup and hasattr(markup, "keyboard"):
                for row in markup.keyboard:
                    for button in row:
                        all_buttons.add(button)
        return all_buttons

    @property
    def last_message_datetime(self) -> Optional[datetime]:
        if self.is_empty:
            return None
        return datetime.fromtimestamp(self.messages[-1].date)

    @property
    def last_message_timestamp(self) -> Optional[time]:
        if self.is_empty:
            return None
        return self.messages[-1].date

    @property
    def commands(self) -> Set[str]:
        all_commands = set()
        for m in self.messages:
            entity_commands = [x for x in m.entities if x.type == "bot_command"]
            for e in entity_commands:
                all_commands.add(m.text[e.offset, len(m.text) - e.length])
            caption_entity_commands = [x for x in m.entities if x.type == "bot_command"]
            for e in caption_entity_commands:
                all_commands.add(m.caption[e.offset, len(m.caption) - e.length])
        return all_commands

    async def delete_all_messages(self, revoke: bool = True):
        peer_id = self.messages[0].chat.id
        await self._controller.client.delete_messages(
            peer_id, [x.message_id for x in self.messages], revoke=revoke
        )

    def __eq__(self, other):
        if not isinstance(other, Response):
            return False

        return (
            self.full_text == other.full_text
            and self.inline_keyboards == other.inline_keyboards
            # TODO: self.keyboard == other.keyboard
        )

    def __getitem__(self, item):
        return self.messages[item]

    def __str__(self):
        if self.is_empty:
            return "Empty response"
        return "\nthen\n".join(['"{}"'.format(m.text) for m in self.messages])


class InvalidResponseError(Exception):
    pass
