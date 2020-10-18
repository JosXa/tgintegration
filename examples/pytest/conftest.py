import asyncio
import logging
from pathlib import Path

import pytest
from decouple import config
from pyrogram import Client

from tgintegration import BotController

examples_dir = Path(__file__).parent.parent

logger = logging.getLogger("tgintegration")
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@pytest.yield_fixture(scope="session", autouse=True)
def event_loop(request):
    """ Create an instance of the default event loop for the session. """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client() -> Client:
    # noinspection PyCallingNonCallable
    client = Client(
        config("SESSION_STRING", default=None) or "tgintegration_examples",
        workdir=examples_dir,
        config_file=str(examples_dir / "config.ini"),
    )
    await client.start()
    yield client
    await client.stop()


@pytest.fixture(scope="module")
async def controller(client):
    c = BotController(
        client=client,
        peer="@BotListBot",
        max_wait=10.0,
        wait_consecutive=0.8,
    )
    await c.initialize(start_client=False)
    yield c
