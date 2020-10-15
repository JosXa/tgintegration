import asyncio
import logging
from pathlib import Path

import pytest

from tgintegration import BotController
from tgintegration import ResponseCollectorClient


logger = logging.getLogger("tgintegration")
logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG)


logging.getLogger("pyrogram").setLevel(logging.WARNING)


@pytest.yield_fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


examples_dir = Path(__file__).parent.parent


@pytest.fixture(scope="session")
async def client() -> ResponseCollectorClient:
    # noinspection PyCallingNonCallable
    client = ResponseCollectorClient(
        "tgintegration_examples",
        config_file=str(examples_dir / "config.ini"),
        workdir=str(examples_dir),
    )
    await client.start()
    yield client
    await client.stop()


@pytest.fixture(scope="module")
async def controller(client):
    c = BotController(
        client=client,
        peer="@BotListBot",
        max_wait_response=10.0,
        min_wait_consecutive=0.8,
    )
    await c.initialize(start_client=False)
    yield c


# @pytest.yield_fixture(scope="session")
# async def controller(event_loop):
#     """
#     Session-scoped fixture that all tests use to receive their BotController instance
#     """
#     print("Initializing...")
#
#     # Using the configuration of `config.ini` (see examples/README)
#     controller = InteractionClient(
#         session_name="my_account",
#         global_action_delay=1.8,  # Space out all messages by 1.8 seconds
#         workdir=examples_dir,  # Load configuration from parent folder
#         config_file=os.path.join(examples_dir, "config.ini"),
#     )
#
#     controller = BotController(
#         peer="@BotListBot",
#         controller=controller,
#         min_wait_consecutive=2.0,  # Wait at least 2 seconds to collect more than one message
#         max_wait=10,  # Wait a max_index of 10 seconds for responses, ...
#         raise_no_response=False,  # ... then check for response.empty instead of raising
#     )
#
#     print("Starting integration test service...")
#     await controller.initialize()
#     # event_loop.run_until_complete(controller.start())
#     print("Client ready.")
#
#     yield controller  # py.test sugar to separate setup from teardown
#
#     # Teardown
#     await controller.stop()
#     # event_loop.run_until_complete(controller.stop())
