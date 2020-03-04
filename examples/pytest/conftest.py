import asyncio
import os
from pathlib import Path

import pytest


from tgintegration import InteractionClient, BotController


@pytest.yield_fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.yield_fixture(scope="session")
async def controller(event_loop):
    """
    Session-scoped fixture that all tests use to receive their BotController instance
    """
    print("Initializing...")
    examples_dir = Path(__file__).parent.parent

    # Using the configuration of `config.ini` (see examples/README)
    client = InteractionClient(
        session_name="my_account",
        global_action_delay=1.8,  # Space out all messages by 1.8 seconds
        workdir=examples_dir,  # Load configuration from parent folder
        config_file=os.path.join(examples_dir, "config.ini"),
    )

    controller = BotController(
        bot_under_test="@BotListBot",
        client=client,
        min_wait_consecutive=2.0,  # Wait at least 2 seconds to collect more than one message
        max_wait_response=10,  # Wait a max of 10 seconds for responses, ...
        raise_no_response=False,  # ... then check for response.empty instead of raising
    )

    print("Starting integration test service...")
    await controller.start()
    # event_loop.run_until_complete(controller.start())
    print("Client ready.")

    yield controller  # py.test sugar to separate setup from teardown

    # Teardown
    await controller.stop()
    # event_loop.run_until_complete(controller.stop())
