import itertools
import re
from typing import List
from typing import Optional
from typing import Pattern
from typing import TYPE_CHECKING
from typing import Union

from pyrogram import filters as f
from pyrogram.raw.types.messages import BotCallbackAnswer
from pyrogram.types import InlineKeyboardButton

from tgintegration.containers.exceptions import NoButtonFound

if TYPE_CHECKING:
    from tgintegration.botcontroller import BotController
    from tgintegration.containers.response import Response


class InlineKeyboard:
    """
    Represents an inline keyboard attached to a message in the Telegram UI and allows to click those buttons.
    """

    def __init__(
        self,
        controller: "BotController",
        chat_id: Union[int, str],
        message_id: int,
        button_rows: List[List[InlineKeyboardButton]],
    ):
        self._controller = controller
        self._message_id = message_id
        self._peer_id = chat_id
        self.rows = button_rows

    def find_button(
        self, pattern: Pattern = None, index: int = None
    ) -> Optional[InlineKeyboardButton]:
        """


        Args:
            pattern ():
            index ():

        Returns:

        """
        index_set = index or index == 0
        if not any((pattern, index_set)) or all((pattern, index_set)):
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
        elif index_set:
            try:
                buttons_flattened = list(itertools.chain.from_iterable(self.rows))

                if index < 0:
                    index += len(buttons_flattened)

                return next(itertools.islice(buttons_flattened, index, index + 1))
            except (StopIteration, ValueError):
                raise NoButtonFound

    async def _click_nowait(self, pattern=None, index=None) -> BotCallbackAnswer:

        button = self.find_button(pattern, index)

        return await self._controller.client.request_callback_answer(
            chat_id=self._peer_id,
            message_id=self._message_id,
            callback_data=button.callback_data,
        )

    async def click(
        self,
        pattern: Union[Pattern, str] = None,
        index: Optional[int] = None,
    ) -> "Response":
        button = self.find_button(pattern, index)

        async with self._controller.collect(
            filters=f.chat(self._peer_id)
        ) as res:  # type: Response
            await self._controller.client.request_callback_answer(
                chat_id=self._peer_id,
                message_id=self._message_id,
                callback_data=button.callback_data,
            )

        return res

    def __eq__(self, other):
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
