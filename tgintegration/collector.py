import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import AsyncContextManager
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from pyrogram.errors import InternalServerError
from pyrogram.filters import Filter
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from tgintegration.handler_utils import add_handler_transient
from tgintegration.utils.sentinel import NotSet

if TYPE_CHECKING:
    from tgintegration.botcontroller import BotController
from tgintegration.containers.response import InvalidResponseError, Response
from tgintegration.update_recorder import MessageRecorder

logger = logging.getLogger(__name__)


@dataclass
class TimeoutSettings:
    max_wait: float = 10
    """
    The maximum duration in seconds to wait for a response from the peer.
    """

    wait_consecutive: Optional[float] = None
    """
    The minimum duration in seconds to wait for another consecutive message from the peer after
    receiving a message. This can cause the total duration to exceed the `max_wait` time.
    """

    raise_on_timeout: bool = False
    """
    Whether to raise an exception when a timeout occurs or to fail with a log message.
    """


@dataclass
class Expectation:
    min_messages: Union[int, NotSet] = NotSet
    max_messages: Union[int, NotSet] = NotSet

    def is_sufficient(self, messages: List[Message]) -> bool:
        n = len(messages)
        if self.min_messages is NotSet:
            return n >= 1
        return n >= self.min_messages

    def _is_match(self, messages: List[Message]) -> bool:
        n = len(messages)
        return (self.min_messages is NotSet or n >= self.min_messages) and (
            self.max_messages is NotSet or n <= self.max_messages
        )

    def verify(self, messages: List[Message], timeouts: TimeoutSettings) -> None:
        if self._is_match(messages):
            return

        n = len(messages)

        if n < self.min_messages:
            _raise_or_log(
                timeouts,
                "Expected {} messages but only received {} after waiting {} seconds.",
                self.min_messages,
                n,
                timeouts.max_wait,
            )
            return

        if n > self.max_messages:
            _raise_or_log(
                timeouts,
                "Expected only {} messages but received {}.",
                self.max_messages,
                n,
            )
            return


@asynccontextmanager
async def collect(
    controller: "BotController",
    filters: Filter = None,
    expectation: Expectation = None,
    timeouts: TimeoutSettings = None,
) -> AsyncContextManager[Response]:
    expectation = expectation or Expectation()
    timeouts = timeouts or TimeoutSettings()

    recorder = MessageRecorder()
    handler = MessageHandler(recorder.record_message, filters=filters)

    assert controller.client.is_connected

    async with add_handler_transient(controller.client, handler):
        response = Response(controller, recorder)

        logger.debug("Collector set up. Executing user-defined interaction...")
        yield response  # Start user-defined interaction
        logger.debug("interaction complete.")

        num_received = 0
        # last_received_timestamp = (
        #     None  # TODO: work with the message's timestamp instead of utcnow()
        # )
        timeout_end = datetime.utcnow() + timedelta(seconds=timeouts.max_wait)

        try:
            seconds_remaining = (timeout_end - datetime.utcnow()).total_seconds()

            while True:
                if seconds_remaining > 0:
                    # Wait until we receive any message or time out
                    logger.debug(f"Waiting for message #{num_received + 1}")
                    await asyncio.wait_for(
                        recorder.wait_until(
                            lambda msgs: expectation.is_sufficient(msgs)
                            or len(msgs) > num_received
                        ),
                        timeout=seconds_remaining,
                    )

                num_received = len(recorder.messages)  # TODO: this is ugly

                if timeouts.wait_consecutive:
                    # Always wait for at least `wait_consecutive` seconds for another message
                    try:
                        logger.debug(
                            f"Checking for consecutive message to #{num_received}..."
                        )
                        await asyncio.wait_for(
                            recorder.wait_until(lambda msgs: len(msgs) > num_received),
                            # The consecutive end may go over the max wait timeout,
                            # which is a design decision.
                            timeout=timeouts.wait_consecutive,
                        )
                        logger.debug("received 1.")
                    except TimeoutError:
                        logger.debug("none received.")

                num_received = len(recorder.messages)  # TODO: this is ugly

                is_sufficient = expectation.is_sufficient(recorder.messages)
                if is_sufficient:
                    expectation.verify(recorder.messages, timeouts)
                    return

                seconds_remaining = (timeout_end - datetime.utcnow()).total_seconds()

                assert seconds_remaining is not None

                if seconds_remaining <= 0:
                    expectation.verify(recorder.messages, timeouts)
                    return

        except InternalServerError as e:
            logger.warning(e)
            await asyncio.sleep(60)  # Internal Telegram error
        except asyncio.exceptions.TimeoutError as te:
            if timeouts.raise_on_timeout:
                raise InvalidResponseError() from te
            else:
                # TODO: better warning message
                logger.warning("Peer did not reply.")
        finally:
            recorder.stop()


def _raise_or_log(timeouts: TimeoutSettings, msg: str, *fmt) -> None:
    if timeouts.raise_on_timeout:
        if fmt:
            raise InvalidResponseError(msg.format(*fmt))
        else:
            raise InvalidResponseError(msg)
    logger.debug(msg, *fmt)
