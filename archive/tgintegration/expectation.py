"""
​
"""
import logging
from dataclasses import dataclass
from typing import List
from typing import Union

from pyrogram.types import Message

from tgintegration.containers.responses import InvalidResponseError
from tgintegration.timeout_settings import TimeoutSettings
from tgintegration.utils.sentinel import NotSet

logger = logging.getLogger(__name__)


@dataclass
class Expectation:
    """
    Defines the expected reaction of a peer.
    """

    min_messages: Union[int, NotSet] = NotSet
    """
    Minimum number of expected messages.
    """

    max_messages: Union[int, NotSet] = NotSet
    """
    Maximum number of expected messages.
    """

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


def _raise_or_log(timeouts: TimeoutSettings, msg: str, *fmt) -> None:
    if timeouts.raise_on_timeout:
        if fmt:
            raise InvalidResponseError(msg.format(*fmt))
        else:
            raise InvalidResponseError(msg)
    logger.debug(msg, *fmt)
