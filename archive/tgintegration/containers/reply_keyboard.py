"""
​
"""
import re
from typing import List
from typing import Pattern
from typing import TYPE_CHECKING
from typing import Union

from pyrogram import filters as f
from pyrogram.filters import Filter
from pyrogram.types import KeyboardButton
from pyrogram.types import Message

from tgintegration.containers import NoButtonFound

if TYPE_CHECKING:
    from tgintegration.botcontroller import BotController
    from tgintegration.containers.responses import Response


class ReplyKeyboard:
    """
    Represents a regular keyboard in the Telegram UI and allows to click buttons in the menu.

    See Also:
        [InlineKeyboard](tgintegration.InlineKeyboard)
    """

    def __init__(
        self,
        controller: "BotController",
        chat_id: Union[int, str],
        message_id: int,
        button_rows: List[List[KeyboardButton]],
    ):
        self._controller: BotController = controller
        self._message_id = message_id
        self._peer_id = chat_id
        self.rows = button_rows

    def find_button(self, pattern: Pattern) -> KeyboardButton:
        """
        Attempts to retrieve a clickable button anywhere in the underlying `rows` by matching the button captions with
        the given `pattern`. If no button could be found, **this method raises** `NoButtonFound`.

        Args:
            pattern: The button caption to look for (by `re.match`).

        Returns:
            The `KeyboardButton` if found.
        """
        compiled = re.compile(pattern)
        for row in self.rows:
            for button in row:
                # TODO: Investigate why sometimes it's a button and other times a string
                if compiled.match(button.text if hasattr(button, "text") else button):
                    return button
        raise NoButtonFound(f"No clickable entity found for pattern r'{pattern}'")

    async def _click_nowait(self, pattern, quote=False) -> Message:
        button = self.find_button(pattern)

        return await self._controller.client.send_message(
            self._peer_id,
            button.text,
            reply_to_message_id=self._message_id if quote else None,
        )

    @property
    def num_buttons(self) -> int:
        """
        Returns the total number of buttons in all underlying rows.
        """
        return sum(len(row) for row in self.rows)

    async def click(
        self, pattern: Pattern, filters: Filter = None, quote: bool = False
    ) -> "Response":
        """
        Uses `find_button` with the given `pattern`, clicks the button if found, and waits for the bot to react. For
        a `ReplyKeyboard`, this means that a message with the button's caption will be sent to the same chat.

        If not button could be found, `NoButtonFound` will be raised.

        Args:
            pattern: The button caption to look for (by `re.match`).
            filters: Additional filters to be given to `collect`. Will be merged with a "same chat" filter and
                `filters.text | filters.edited`.
            quote: Whether to reply to the message containing the buttons.

        Returns:
            The bot's `Response`.
        """
        button = self.find_button(pattern)

        filters = (
            filters & f.chat(self._peer_id) if filters else f.chat(self._peer_id)
        ) & (f.text | f.edited)

        async with self._controller.collect(filters=filters) as res:  # type: Response
            await self._controller.client.send_message(
                self._controller.peer,
                button.text if hasattr(button, "text") else button,
                reply_to_message_id=self._message_id if quote else None,
            )

        return res
