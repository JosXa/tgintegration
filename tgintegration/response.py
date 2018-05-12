import re
import time
from datetime import datetime

from pyrogram import Filters, InlineKeyboardMarkup
from pyrogram.client.types.reply_markup.reply_keyboard_markup import ReplyKeyboardMarkup

from tgintegration.awaitableaction import AwaitableAction
from tgintegration.containers import InlineKeyboard, ReplyKeyboard


class Response:
    def __init__(self, client, to_action):
        self.client = client
        self.action = to_action

        self.started = None
        self.action_result = None
        self._messages = []

        # cached properties
        self.__reply_keyboard = None
        self.__inline_keyboards = None

    @property
    def messages(self):
        return self._messages

    def _add_message(self, message):
        message.exact_timestamp = time.time()
        self._messages.append(message)

    @property
    def empty(self):
        return not self._messages

    @property
    def num_messages(self):
        return len(self._messages)

    @property
    def full_text(self):
        return '\n'.join(x.text for x in self._messages if x.text) or ''

    def press_inline_button(self, pattern):
        pattern = re.compile(pattern)
        for m in self._messages:
            markup = m.reply_markup
            if markup and hasattr(markup, 'inline_keyboard'):
                for row in markup.inline_keyboard:
                    for button in row:
                        if pattern.match(button.text):
                            chat_id = m.chat.id

                            action = AwaitableAction(
                                func=self.client.press_inline_button,
                                args=(chat_id, m, bytes(button.callback_data, "utf-8")),
                                filters=Filters.chat(chat_id),
                                max_wait=10,
                                min_wait_consecutive=3
                            )
                            return self.client.act_await_response(action)
        raise ValueError("No button found.")

    @property
    def reply_keyboard(self):
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
            client=self.client,
            chat_id=last_kb_msg.chat.id,
            message_id=last_kb_msg.message_id,
            button_rows=last_kb_msg.reply_markup.keyboard
        )
        self.__reply_keyboard = reply_keyboard
        return reply_keyboard

    @property
    def inline_keyboards(self):
        if self.__inline_keyboards:
            return self.__inline_keyboards
        if self.empty:
            return None

        inline_keyboards = []

        for message in self.messages:
            if isinstance(message.reply_markup, InlineKeyboardMarkup):
                inline_keyboards.append(
                    InlineKeyboard(
                        client=self.client,
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        button_rows=message.reply_markup.inline_keyboard
                    )
                )

        self.__inline_keyboards = inline_keyboards
        return inline_keyboards

    @property
    def keyboard_buttons(self):
        all_buttons = set()
        for m in self._messages:
            markup = m.reply_markup
            if markup and hasattr(markup, 'keyboard'):
                for row in markup.keyboard:
                    for button in row:
                        all_buttons.add(button)
        return all_buttons

    @property
    def last_message_timestamp(self):
        if self.empty:
            return None
        # TODO: Dan should fix this
        return datetime.fromtimestamp(self._messages[-1].date)

    def __getitem__(self, item):
        return self._messages[item]

    def __str__(self):
        if self.empty:
            return "Empty response"
        return '\nthen\n'.join(['"{}"'.format(m.text) for m in self._messages])


class InvalidResponseError(Exception):
    pass
