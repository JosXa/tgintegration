from collections import OrderedDict
from contextlib import asynccontextmanager
from typing import List

from pyrogram import Client
from pyrogram.dispatcher import Dispatcher
from pyrogram.handlers.handler import Handler


def find_free_group(dispatcher: Dispatcher, max_index: int = -1000) -> int:
    """
    Finds the next free group index in the given `dispatcher`'s groups that is lower than `max_index`.
    """
    groups = dispatcher.groups
    i = max_index
    while True:
        if i in groups:
            i -= 1
            continue
        return i


@asynccontextmanager
async def add_handlers_transient(client: Client, handlers: List[Handler]):
    dispatcher = client.dispatcher

    # TODO: Add a comment why it's necessary to circumvent pyro's builtin
    for lock in dispatcher.locks_list:
        await lock.acquire()

    group = find_free_group(dispatcher)

    try:
        dispatcher.groups[group] = []
        dispatcher.groups = OrderedDict(sorted(dispatcher.groups.items()))
        for handler in handlers:
            dispatcher.groups[group].append(handler)
    finally:
        for lock in dispatcher.locks_list:
            lock.release()

    yield

    for lock in dispatcher.locks_list:
        await lock.acquire()

    try:
        if group not in dispatcher.groups:
            raise ValueError(f"Group {group} does not exist. Handler was not removed.")

        for handler in handlers:
            dispatcher.groups[group].remove(handler)
    finally:
        for lock in dispatcher.locks_list:
            lock.release()
