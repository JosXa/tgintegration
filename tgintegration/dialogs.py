import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncIterator, Optional

from pyrogram import Client
from pyrogram.errors import RpcMcgetFail
from pyrogram.filters import Filter
from pyrogram.handlers import MessageHandler

from tgintegration.containers.response import InvalidResponseError, Response
from . import AwaitableAction
from ._handler_utils import add_handler_transient
from .actors import TimeoutSettings
from .responsecollectorclient import SLEEP_DURATION
from .update_recorder import MessageRecorder


class Dialog:
    def __init__(self, recorder: MessageRecorder):
        self.recorder = recorder


@asynccontextmanager
def start_dialog(
    client: Client, filters: Filter = None, timeouts: TimeoutSettings = None
) -> AsyncIterator[Dialog]:
    timeouts = timeouts or TimeoutSettings()

    recorder = MessageRecorder()
    handler = MessageHandler(recorder.record_message, filters=filters)

    with add_handler_transient(client, handler):
        dialog = Dialog(recorder)
        yield dialog
