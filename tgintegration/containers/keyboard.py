import itertools
import re
import weakref
from typing import Union, List, Pattern, Optional, TYPE_CHECKING

from pyrogram import Client, filters
from pyrogram.raw.types.messages import BotCallbackAnswer
from pyrogram.types import InlineKeyboardButton, KeyboardButton, Message

from tgintegration import AwaitableAction

if TYPE_CHECKING:
    from tgintegration import Response


class ReplyKeyboard:
    def __init__(
        self,
        client: Client,
        chat_id: Union[int, str],
        message_id: int,
        button_rows: List[List[KeyboardButton]],
    ):
        self._client = weakref.proxy(client)
        self._message_id = message_id
        self._peer_id = chat_id
        self.rows = button_rows

    def find_button(self, pattern) -> Optional[KeyboardButton]:
        compiled = re.compile(pattern)
        for row in self.rows:
            for button_text in row:
                if compiled.match(button_text):
                    return button_text
        raise NoButtonFound(f"No clickable entity found for pattern r'{pattern}'")

    async def press_button(self, pattern, quote=False) -> Message:
        button = self.find_button(pattern)

        return await self._client.send_message(
            self._peer_id,
            button,
            reply_to_message_id=self._message_id if quote else None,
        )

    @property
    def num_buttons(self) -> int:
        return sum(len(row) for row in self.rows)

    async def press_button_await(
        self, pattern, filters=None, num_expected=None, raise_=True, quote=False
    ) -> "Response":
        button = self.find_button(pattern)

        if filters:
            filters = filters & filters.chat(self._peer_id)
        else:
            filters = filters.chat(self._peer_id)

        filters = filters & (filters.text | filters.edited)

        action = AwaitableAction(
            func=self._client.send_message,
            args=(self._peer_id, button),
            kwargs=dict(reply_to_message_id=self._message_id if quote else None),
            filters=filters,
            num_expected=num_expected,
        )
        return await self._client.act_await_response(action, raise_=raise_)


class InlineKeyboard:
    def __init__(
        self,
        client: Client,
        chat_id: Union[int, str],
        message_id: int,
        button_rows: List[List[InlineKeyboardButton]],
    ):
        self._client = weakref.proxy(client)
        self._message_id = message_id
        self._peer_id = chat_id
        self.rows = button_rows

    def find_button(self, pattern=None, index=None) -> Optional[InlineKeyboardButton]:
        if not any((pattern, index)) or all((pattern, index)):
            raise ValueError(
                "Exactly one of the `pattern` or `index` arguments must be provided."
            )

        if pattern:
            compiled = re.compile(pattern)
            for row in self.rows:
                for button in row:
                    if compiled.match(button.text):
                        return button
            raise NoButtonFound
        elif index:
            try:
                return next(
                    itertools.islice(
                        itertools.chain.from_iterable(self.rows), index, index + 1
                    )
                )
            except StopIteration:
                raise NoButtonFound

    async def press_button(self, pattern=None, index=None) -> BotCallbackAnswer:

        button = self.find_button(pattern, index)

        return await self._client.press_inline_button(
            chat_id=self._peer_id,
            on_message=self._message_id,
            callback_data=button.callback_data,
        )

    async def press_button_await(
        self,
        pattern: Union[Pattern, str] = None,
        index: Optional[int] = None,
        num_expected: Optional[int] = None,
        max_wait: float = 8,
        min_wait_consecutive: float = 1.5,
        raise_: Optional[bool] = True,
    ):
        button = self.find_button(pattern, index)

        action = AwaitableAction(
            func=self._client.press_inline_button,
            args=(self._peer_id, self._message_id, button.callback_data),
            filters=filters.chat(self._peer_id),
            num_expected=num_expected,
            max_wait=max_wait,
            min_wait_consecutive=min_wait_consecutive,
        )
        return await self._client.act_await_response(action, raise_=raise_)

    def __eq__(self, other):
        # TODO: test
        if not isinstance(other, InlineKeyboard):
            return False
        try:
            for r_n, row in enumerate(self.rows):
                other_row = other.rows[r_n]
                for b_n, btn in enumerate(row):
                    other_btn = other_row[b_n]
                    if (
                        btn.text != other_btn.text
                        or btn.switch_inline_query_current_chat
                        != other_btn.switch_inline_query_current_chat
                        or btn.switch_inline_query != other_btn.switch_inline_query
                        or btn.callback_data != other_btn.callback_data
                        or btn.url != other_btn.url
                    ):
                        return False
        except KeyError:
            return False

        return True

    @property
    def num_buttons(self):
        return sum(len(row) for row in self.rows)


class NoButtonFound(Exception):
    pass
