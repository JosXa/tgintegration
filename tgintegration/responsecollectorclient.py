import asyncio
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    ClassVar,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    AbstractSet,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    AsyncIterator,
    AsyncIterable,
    Coroutine,
    Collection,
    AsyncGenerator,
    Deque,
    Dict,
    List,
    Set,
    FrozenSet,
    NamedTuple,
    Generator,
    cast,
    overload,
    TYPE_CHECKING,
)
from typing_extensions import TypedDict

import logging
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta
from typing import Optional, Iterator, Tuple, AsyncIterator

from pyrogram import Client
from pyrogram.errors import RpcMcgetFail
from pyrogram.filters import Filter
from pyrogram.handlers.handler import Handler
from typing_extensions import Final

from tgintegration.containers.response import InvalidResponseError, Response
from .awaitableaction import AwaitableAction


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


