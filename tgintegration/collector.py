"""
Standalone `collector` utilities.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from datetime import timedelta
from typing import AsyncContextManager
from typing import TYPE_CHECKING

from pyrogram.errors import InternalServerError
from pyrogram.filters import Filter
from pyrogram.handlers import EditedMessageHandler, MessageHandler

from tgintegration.expectation import Expectation
from tgintegration.handler_utils import add_handlers_transient
from tgintegration.timeout_settings import TimeoutSettings

if TYPE_CHECKING:
    from tgintegration.botcontroller import BotController

from tgintegration.containers.responses import InvalidResponseError, Response
from tgintegration.update_recorder import MessageRecorder

logger = logging.getLogger(__name__)


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
    message_handler = MessageHandler(recorder.record_message, filters=filters)
    edited_message_handler = EditedMessageHandler(
        recorder.record_message, filters=filters
    )

    assert controller.client.is_connected

    async with add_handlers_transient(
        controller.client, [message_handler, edited_message_handler]
    ):
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

                if expectation.is_sufficient(recorder.messages):
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
