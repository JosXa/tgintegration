"""
Controller
"""
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import cast
from typing import List
from typing import Optional
from typing import Union

from pyrogram import Client
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.filters import Filter
from pyrogram.handlers.handler import Handler
from pyrogram.raw.base import BotCommand
from pyrogram.raw.functions.channels import DeleteHistory
from pyrogram.raw.functions.users import GetFullUser
from pyrogram.raw.types import BotInfo
from pyrogram.types import Message
from pyrogram.types import User
from typing_extensions import AsyncContextManager

from tgintegration._handler_utils import add_handler_transient
from tgintegration.collector import collect
from tgintegration.collector import Expectation
from tgintegration.collector import NotSet
from tgintegration.collector import TimeoutSettings
from tgintegration.containers.response import Response


class BotController:
    """
    This class is the entry point for all interactions with either regular bots or userbots in `TgIntegration`.
    It expects a Pyrogram `Client` (typically a **user client**) which serves as the controll**ing** account for a
    specific `peer` account, which can be seen as the "bot under test" or "conversation partner".
    In addition, the controller holds a number of settings to control the timeouts for all these interactions.
    """

    def __init__(
        self,
        client: Client,
        peer: Union[int, str],
        *,
        max_wait: Union[int, float] = 20.0,
        wait_consecutive: Optional[Union[int, float]] = 2.0,
        raise_no_response: bool = True,
        global_action_delay: Union[int, float] = 0.8,
    ):
        """
        Creates a new `BotController`.

        Args:
            client: A Pyrogram user client that acts as the controll*ing* account.
            peer: The bot under test or conversation partner.
            max_wait: Maximum time in seconds for the `peer` to produce the expected response.
            wait_consecutive: Additional time in seconds to wait for _additional_ messages upon receiving a response
                (even when `max_wait` is exceeded).
            raise_no_response: Whether to raise an exception on timeout/invalid response or to log silently.
            global_action_delay: TODO: Not yet implemented
        """
        self.client = client
        self.peer = peer
        self.max_wait_response = max_wait
        self.min_wait_consecutive = wait_consecutive
        self.raise_no_response = raise_no_response
        self.global_action_delay = global_action_delay

        self.peer_user: Optional[User] = None
        self.peer_id: Optional[int] = None
        self.command_list: List[BotCommand] = []

        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self, start_client: bool = True) -> None:
        # noinspection PyUnresolvedReferences
        """
        Fetches and caches information about the given `peer` and optionally starts the assigned `client`.
        This method will automatically be called when coroutines of this class are invoked, but you can call it
        manually to override defaults (namely whether to `start_client`).

        Args:
            start_client: Set to `False` if the client should not be started as part of initialization.

        !!! note
            It is unlikely that you will need to call this manually.
        """
        if start_client and not self.client.is_connected:
            await self.client.start()

        self.peer_user = await self.client.get_users(self.peer)
        self.peer_id = self.peer_user.id
        self.command_list = await self._get_command_list()

    async def _ensure_initialized(self):
        if not self.peer_id:
            await self.initialize()

    def _merge_default_filters(
        self, user_filters: Filter = None, override_peer: Union[int, str] = None
    ) -> Filter:
        chat_filter = filters.chat(override_peer or self.peer_id) & filters.incoming
        if user_filters is None:
            return chat_filter
        else:
            return user_filters & chat_filter

    async def _get_command_list(self) -> List[BotCommand]:
        return list(
            cast(
                BotInfo,
                (
                    await self.client.send(
                        GetFullUser(id=await self.client.resolve_peer(self.peer_id))
                    )
                ).bot_info,
            ).commands
        )

    async def clear_chat(self) -> None:
        """
        Deletes all messages in the conversation with the assigned `peer`.

        !!! warning
            Be careful as this will completely drop your mutual message history.
        """
        await self.client.send(
            DeleteHistory(peer=self.peer_user, max_id=0, just_clear=False)
        )

    async def _wait_global(self):
        if self.global_action_delay and self._last_response:
            # Sleep for as long as the global delay prescribes
            sleep = self.global_action_delay - (
                time.time() - self._last_response.started
            )
            if sleep > 0:
                await asyncio.sleep(sleep)

    @asynccontextmanager
    async def add_handler_transient(
        self, handler: Handler
    ) -> AsyncContextManager[None]:
        """
        Registers a one-time/ad-hoc Pyrogram `Handler` that is only valid during the context manager body.

        Args:
            handler: A Pyrogram `Handler` (typically a `MessageHandler`).

        Yields:
            `None`

        Examples:
            ``` python
            async def some_callback(client, message):
                print(message)

            async def main():
                async with controller.add_handler_transient(MessageHandler(some_callback, filters.text)):
                    await controller.send_command("start")
            ```
        """
        async with add_handler_transient(self.client, handler):
            yield

    @asynccontextmanager
    async def collect(
        self,
        filters: Filter = None,
        count: int = None,
        *,
        peer: Union[int, str] = None,
        max_wait: Union[int, float] = 15,
        wait_consecutive: Optional[Union[int, float]] = None,
    ) -> AsyncContextManager[Response]:
        await self._ensure_initialized()
        async with collect(
            self,
            self._merge_default_filters(filters, peer),
            expectation=Expectation(
                min_messages=count or NotSet, max_messages=count or NotSet
            ),
            timeouts=TimeoutSettings(
                max_wait=max_wait, wait_consecutive=wait_consecutive
            ),
        ) as response:
            yield response

    async def ping_bot(
        self,
        override_messages: List[str] = None,
        override_filters: Filter = None,
        *,
        peer: Union[int, str] = None,
        max_wait: Union[int, float] = 15,
        wait_consecutive: Optional[Union[int, float]] = None,
    ) -> Response:
        await self._ensure_initialized()
        peer = peer or self.peer_id

        messages = ["/start"]
        if override_messages:
            messages = override_messages

        async def send_pings():
            for n, m in enumerate(messages):
                try:
                    if n >= 1:
                        await asyncio.sleep(1)
                    await self.send_command(m, peer=peer)
                except FloodWait as e:
                    if e.x > 5:
                        self.logger.warning(
                            "send_message flood: waiting {} seconds".format(e.x)
                        )
                    await asyncio.sleep(e.x)
                    continue

        async with collect(
            self,
            self._merge_default_filters(override_filters, peer),
            expectation=Expectation(min_messages=1),
            timeouts=TimeoutSettings(
                max_wait=max_wait, wait_consecutive=wait_consecutive
            ),
        ) as response:
            await send_pings()

        return response

    async def send_command(
        self,
        command: str,
        args: List[str] = None,
        peer: Union[int, str] = None,
        add_bot_name: bool = True,
    ) -> Message:
        """
        Send a slash-command with corresponding parameters.
        """
        text = "/" + command.lstrip("/")

        if add_bot_name and self.peer_user.username:
            text += f"@{self.peer_user.username}"

        if args:
            text += " "
            text += " ".join(args)

        return await self.client.send_message(peer or self.peer_id, text)
