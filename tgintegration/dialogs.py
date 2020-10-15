from contextlib import asynccontextmanager
from typing import AsyncIterator

from pyrogram import Client
from pyrogram.filters import Filter
from pyrogram.handlers import MessageHandler

from tgintegration._handler_utils import add_handler_transient
from tgintegration.collector import TimeoutSettings
from tgintegration.update_recorder import MessageRecorder


class Dialog:
    def __init__(self, recorder: MessageRecorder):
        self.recorder = recorder


@asynccontextmanager
async def start_dialog(
    client: Client, filters: Filter = None, timeouts: TimeoutSettings = None
) -> AsyncIterator[Dialog]:
    timeouts = timeouts or TimeoutSettings()

    recorder = MessageRecorder()
    handler = MessageHandler(recorder.record_message, filters=filters)

    async with add_handler_transient(client, handler):
        dialog = Dialog(recorder)
        yield dialog
