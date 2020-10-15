import asyncio
import logging
import time

from pyrogram.types import Message, Update
from typing import (
    Any,
    Awaitable,
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


logger = logging.getLogger(__name__)


class MessageRecorder:
    def __init__(self):
        self.messages: List[Message] = []
        self._lock = asyncio.Lock()

        self.any_received = asyncio.Event()
        self._event_conditions: List[
            Tuple[Callable[[List[Message]], bool], asyncio.Event]
        ] = [(bool, self.any_received)]

        self._is_completed = False

    async def record_message(self, _, message: Message):
        if self._is_completed:
            return

        async with self._lock:
            message.exact_timestamp = time.time()
            self.messages.append(message)
            for (pred, ev) in self._event_conditions:
                if pred(self.messages):
                    ev.set()

    async def wait_until(self, predicate: Callable[[List[Message]], bool]):

        async with self._lock:
            if predicate(self.messages):
                return

            ev = asyncio.Event()
            self._event_conditions.append((predicate, ev))

        await ev.wait()

    def stop(self):
        self._is_completed = True

