import asyncio

import pytest
from decouple import config
from tgintegration.interactionclient import InteractionClient


@pytest.yield_fixture(scope="module")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def client() -> InteractionClient:
    # noinspection PyCallingNonCallable
    client = InteractionClient(config("SESSION_STRING"), config_file="config.ini")
    await client.start()
    yield client
    await client.stop()
