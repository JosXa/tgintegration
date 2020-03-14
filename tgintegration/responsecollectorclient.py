import asyncio
import logging
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional, Iterator, Tuple, AsyncIterator

from async_generator import asynccontextmanager
from pyrogram import Client, MessageHandler
from pyrogram.client.filters.filter import Filter
from pyrogram.client.handlers.handler import Handler
from pyrogram.errors import RpcMcgetFail
from typing_extensions import Final

from tgintegration.containers.response import InvalidResponseError, Response
from .awaitableaction import AwaitableAction

SLEEP_DURATION: Final[float] = 0.15


class ResponseCollectorClient(Client):
    def __init__(self, *args, global_action_delay=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.global_action_delay = global_action_delay
        self._last_response = None

    async def _wait_global(self):
        if self.global_action_delay and self._last_response:
            # Sleep for as long as the global delay prescribes
            sleep = self.global_action_delay - (
                time.time() - self._last_response.started
            )
            if sleep > 0:
                await asyncio.sleep(sleep)

    def _add_handler_nolock(
        self, handler: Handler, group: int = None
    ) -> Tuple[Handler, int]:
        """Add handler to empty group manually, as the Pyrogram lock seems to never release when trying to use
        .add_handler at runtime."""
        # TODO: find next empty group if group is None
        group = group or -99
        if group not in self.dispatcher.groups:
            self.dispatcher.groups[group] = []
        self.dispatcher.groups[group].append(handler)
        return handler, group

    def _remove_handler_nolock(self, handler: Handler, group: int) -> None:
        self.dispatcher.groups[group].remove(handler)

    @contextmanager
    def expect(
        self,
        filters: Filter = None,
        count: int = None,
        max_wait: float = None,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
    ) -> AsyncIterator[Response]:
        pass

    @asynccontextmanager
    async def collect(self, action: AwaitableAction) -> Iterator[Response]:
        response = Response(self)

        async def collect(_, message):
            # noinspection PyProtectedMember
            response._add_message(message)

        handler = MessageHandler(callback=collect, filters=action.filters)

        h = self._add_handler_nolock(handler)

        # Start timer
        response.started = time.time()

        # Execute the action
        response.action_result = await action.func(*action.args, **action.kwargs)

        yield response

        self._remove_handler_nolock(*h)

    async def act_await_response(
        self, action: AwaitableAction, raise_=True
    ) -> Optional[Response]:

        await self._wait_global()

        async with self.collect(action) as response:
            try:
                # Calculate maximum wait time
                timeout_end = datetime.now() + timedelta(seconds=action.max_wait)

                # Wait for the first reply
                while response.empty:

                    if time.time() - response.started > 5:
                        self.logger.debug("No response received yet after 5 seconds")

                    if datetime.now() > timeout_end:
                        msg = "Aborting because no response was received after {} seconds.".format(
                            action.max_wait
                        )

                        if raise_:
                            raise InvalidResponseError(msg)
                        else:
                            self.logger.debug(msg)
                            return response

                    await asyncio.sleep(SLEEP_DURATION)

                # A response was received
                if action.consecutive_wait:
                    # Wait for more consecutive messages from the peer
                    consecutive_delta = timedelta(seconds=action.consecutive_wait)

                    while True:
                        now = datetime.now()

                        if action.num_expected is not None:
                            # User has set explicit number of messages to await
                            if response.num_messages < action.num_expected:
                                # Less messages than expected (so far)
                                if now > timeout_end:
                                    # Timed out
                                    msg = (
                                        "Expected {} messages but only received {} "
                                        "after waiting {} seconds.".format(
                                            action.num_expected,
                                            response.num_messages,
                                            action.max_wait,
                                        )
                                    )

                                    if (
                                        raise_
                                    ):  # TODO: should this really be toggleable? raise always?
                                        raise InvalidResponseError(msg)
                                    else:
                                        self.logger.debug(msg)
                                        return None
                                # else: continue

                            elif response.num_messages > action.num_expected:
                                # More messages than expected
                                msg = "Expected {} messages but received {}.".format(
                                    action.num_expected, response.num_messages
                                )

                                if (
                                    raise_
                                ):  # TODO: should this really be toggleable? raise always?
                                    raise InvalidResponseError(msg)
                                else:
                                    self.logger.debug(msg)
                                    return None
                            else:
                                self._last_response = response
                                return response
                        else:
                            # User has not provided an expected number of messages
                            if (
                                now
                                > (response.last_message_timestamp + consecutive_delta)
                                or now > timeout_end
                            ):
                                self._last_response = response
                                return response

                        await asyncio.sleep(SLEEP_DURATION)

                self._last_response = response
                return response

            except RpcMcgetFail as e:
                self.logger.warning(e)
                await asyncio.sleep(60)  # Internal Telegram error
