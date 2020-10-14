import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import (
    ContextManager,
    List,
    Optional,
    Union,
    cast,
)

from pyrogram import Client, filters
from pyrogram.filters import Filter
from pyrogram.handlers.handler import Handler
from pyrogram.raw.base import BotCommand
from pyrogram.raw.functions.channels import DeleteHistory
from pyrogram.raw.functions.users import GetFullUser
from pyrogram.raw.types import BotInfo, PeerUser
from typing_extensions import AsyncContextManager

from tgintegration._handler_utils import add_handler_transient
from tgintegration.collector import Expectation, TimeoutSettings, collect
from tgintegration.containers.response import Response


class BotController:
    def __init__(
        self,
        client: Client,
        peer: Union[int, str],
        *,
        max_wait_response: Union[int, float] = 20.0,
        min_wait_consecutive: Optional[Union[int, float]] = 2.0,
        raise_no_response: bool = True,
        global_action_delay: Union[int, float] = 0.8,
    ):
        self.client = client
        self.peer = peer
        self.max_wait_response = max_wait_response
        self.min_wait_consecutive = min_wait_consecutive
        self.raise_no_response = raise_no_response
        self.global_action_delay = global_action_delay

        self.peer_user: Optional[PeerUser] = None
        self.peer_id: Optional[int] = None
        self.command_list: List[BotCommand] = []

        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self, start_client: bool = True):
        if start_client and not self.client.is_connected:
            await self.client.start()

        self.peer_user = await self.client.resolve_peer(self.peer)
        self.peer_id = self.peer_user.user_id
        self.command_list = await self._get_command_list()

    async def _ensure_initialized(self):
        if not self.peer_id:
            await self.initialize()

    # async def ping_bot(
    #     self,
    #     override_messages: List[str] = None,
    #     max_wait_response: float = None,
    #     wait_consecutive: float = None,
    # ) -> Union[Response, bool]:
    #     messages = ["/start"]
    #     if override_messages:
    #         messages = override_messages
    #
    #     async def send_pings():
    #         for n, m in enumerate(messages):
    #             try:
    #                 if n >= 1:
    #                     await asyncio.sleep(1)
    #                 await self.client.send_message(self.peer, m)
    #             except FloodWait as e:
    #                 if e.x > 5:
    #                     self.logger.warning(
    #                         "send_message flood: waiting {} seconds".format(e.x)
    #                     )
    #                 await asyncio.sleep(e.x)
    #                 continue
    #
    #     action = AwaitableAction(
    #         send_pings,
    #         filters=filters.chat(peer_user),
    #         max_wait=max_wait_response,
    #         wait_consecutive=wait_consecutive,
    #     )
    #
    #     return await self.act_await_response(action)

    def merge_default_filters(self, user_filters: Filter = None) -> Filter:
        chat_filter = filters.chat(self.peer_id) & filters.incoming
        if user_filters is None:
            return chat_filter
        else:
            return user_filters & chat_filter

    async def _get_command_list(self) -> List[BotCommand]:
        return list(
            cast(
                BotInfo,
                (await self.client.send(GetFullUser(id=self.peer_user))).bot_info,
            ).commands
        )

    async def clear_chat(self) -> None:
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

    def add_handler_transient(self, handler: Handler) -> ContextManager[None]:
        return add_handler_transient(self.client, handler)

    @asynccontextmanager
    async def collect(
        self,
        filters: Filter = None,
        count: int = None,
        *,
        peer: Union[int, str] = None,
        max_wait: Union[int, float] = 20,
        wait_consecutive: Optional[Union[int, float]] = None,
    ) -> AsyncContextManager[Response]:
        await self._ensure_initialized()
        async with collect(
            self.client,
            self.merge_default_filters(filters),
            expectation=Expectation(num_messages=count),
            timeouts=TimeoutSettings(
                max_wait=max_wait, wait_consecutive=wait_consecutive
            ),
        ) as response:
            yield response
