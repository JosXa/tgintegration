import re
from datetime import datetime
from typing import List, Pattern, Set

from pyrogram import Message, Filters
from tgintegration.awaitableaction import AwaitableAction


class Response:
    def __init__(self, client: 'InteractionClient', to_action: AwaitableAction):
        self.client = client
        self.action = to_action

        self.started = None  # type: float
        self.action_result = None
        self._messages = []  # type: List[Message]

    @property
    def messages(self) -> List[Message]:
        return self._messages

    def _add_message(self, message: Message):
        self._messages.append(message)

    @property
    def empty(self) -> bool:
        return not self._messages

    @property
    def num_messages(self) -> int:
        return len(self._messages)

    @property
    def full_text(self):
        return '\n'.join(x.text for x in self._messages if x.text) or ''

    def press_inline_button(self, pattern: Pattern):
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
    def keyboard_buttons(self) -> Set[str]:
        all_buttons = set()
        for m in self._messages:
            markup = m.reply_markup
            if markup and hasattr(markup, 'keyboard'):
                for row in markup.keyboard:
                    for button in row:
                        all_buttons.add(button)
        return all_buttons

    @property
    def last_message_timestamp(self) -> datetime:
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
