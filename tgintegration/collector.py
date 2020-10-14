import asyncio
import logging
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import AsyncContextManager, Callable, Generator, List, Optional

from pyrogram import Client
from pyrogram.errors import RpcMcgetFail
from pyrogram.filters import Filter
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from tgintegration._handler_utils import add_handler_transient
from tgintegration.containers.response import InvalidResponseError, Response
from tgintegration.update_recorder import MessageRecorder

logger = logging.getLogger(__name__)


@dataclass
class TimeoutSettings:
    max_wait: float = 10,
    wait_consecutive: Optional[float] = None
    raise_: bool = False


@dataclass
class Expectation:
    num_messages: Optional[int] = None

    def to_predicate(self) -> Callable[[List[Message]], bool]:
        def fn(updates: List[Message]):
            return len(updates) == self.num_messages

        return fn


# class Collector(AbstractAsyncContextManager):
#     def __init__(self,
#                  client: Client,
#                  filters: Filter = None,
#                  expectation: Expectation = None,
#                  timeouts: TimeoutSettings = None
#                  ):
#         self.client = client
#         self.filters = filters
#         self.expectation = expectation or Expectation()
#         self.timeouts = timeouts or TimeoutSettings()
#         self.recorder = MessageRecorder()
#         self.response: Optional[Response] = None
#
#     async def __aenter__(self):
#         handler = MessageHandler(self.recorder.record_message, filters=self.filters)
#
#         with add_handler_transient(self.client, handler):
#             self.response = Response(self.client, self.recorder)
#             self.response._messages = self.recorder.messages
#             return self.response
#
#     async def __aexit__(self, exc_type, exc_value, traceback):
#         pass


@asynccontextmanager
async def collect(
    client: Client,
    filters: Filter = None,
    expectation: Expectation = None,
    timeouts: TimeoutSettings = None
) -> AsyncContextManager[Response]:
    expectation = expectation or Expectation()
    timeouts = timeouts or TimeoutSettings()

    recorder = MessageRecorder()
    handler = MessageHandler(recorder.record_message, filters=filters)

    with add_handler_transient(client, handler):
        response = Response(client, recorder)
        response._messages = recorder.messages
        yield response

        # User interaction done
        timeout_end = datetime.utcnow() + timedelta(seconds=timeouts.max_wait)

        try:
            # Wait for the first reply
            await asyncio.wait_for(recorder.any_received.wait(), timeout=timeouts.max_wait)

            # A response has been received
            if timeouts.wait_consecutive is not None:
                # Wait for more consecutive messages from the peer_user
                consecutive_delta = timedelta(seconds=timeouts.wait_consecutive)

            while True:
                now = datetime.utcnow()

                if expectation.num_messages:
                    if response.num_messages < expectation.num_messages:
                        # Less messages than expected (so far)
                        if now > timeout_end:
                            # Timed out

                            raise_or_log(
                                timeouts,
                                "Expected {} messages but only received {} after waiting {} seconds.",
                                expectation.num_messages,
                                response.num_messages,
                                timeouts.max_wait
                            )
                            return

                    else:
                        if response.num_messages > expectation.num_messages:
                            # More messages than expected
                            raise_or_log(timeouts, "Expected {} messages but received {}.",
                                         expectation.num_messages, response.num_messages)
                        return
                else:
                    # User has not provided an expected number of messages
                    if (
                        now
                        > (response.last_message_timestamp + consecutive_delta)
                        or now > timeout_end
                    ):
                        return

                await asyncio.sleep(SLEEP_DURATION)

            return

        except RpcMcgetFail as e:
            logger.warning(e)
            await asyncio.sleep(60)  # Internal Telegram error
        finally:
            recorder.stop()


def raise_or_log(timeouts: TimeoutSettings, msg: str, *fmt) -> None:
    if timeouts.raise_:
        if fmt:
            raise InvalidResponseError(msg.format(*fmt))
        else:
            raise InvalidResponseError(msg)
    logger.debug(msg, *fmt)
