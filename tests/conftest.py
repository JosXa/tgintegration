import asyncio

import pytest
from decouple import config
from pyrogram import Client

# region TODO: These fixtures are currently unused until we have some basic integration tests.
#              The idea would be to spin up a bot client and a user client that talk to each other in a
#              controlled fashion.


@pytest.yield_fixture(scope="module")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def client() -> Client:
    # noinspection PyCallingNonCallable
    client = Client(config("SESSION_STRING"), config_file="config.ini")
    await client.start()
    yield client
    await client.stop()


# endregion
