from contextlib import asynccontextmanager, contextmanager
from typing import AsyncIterator

from pyrogram import Client
from pyrogram.dispatcher import Dispatcher
from pyrogram.handlers.handler import Handler


def find_free_group(dispatcher: Dispatcher, max_index: int = -1000) -> int:
    """
    Finds the next free group index in the given `dispatcher`'s groups that is lower than `max_index`.
    """
    current_lowest = min(iter(dispatcher.groups.keys()), default=max_index)
    return min(current_lowest - 1, max_index)


@contextmanager
def add_handler_transient(
    client: Client, handler: Handler
):
    dispatcher = client.dispatcher
    group = find_free_group(dispatcher)

    dispatcher.add_handler(handler, group)
    yield
    dispatcher.remove_handler(handler, group)

    # TODO: Remove if this works
    # async with dispatcher.locks_list[-1]:
    #     dispatcher.groups.setdefault(group, []).append(handler)
    # async with dispatcher.locks_list[-1]:
    #     dispatcher.remove_handler(handler, group)

