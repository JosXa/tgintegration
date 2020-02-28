import os
from pathlib import Path

import pytest

from tgintegration import BotIntegrationClient


# Create a session-scoped fixture that all tests use to receive their BotIntegrationClient instance
@pytest.yield_fixture(scope="session")
def client():
    # Setup
    print('Initializing BotIntegrationClient')

    examples_dir = Path(__file__).parent.parent

    c = BotIntegrationClient(
        session_name='tgintegration_examples',
        bot_under_test='@BotListBot',  # We're going to test the @BotListBot
        max_wait_response=10,  # Wait a max of 10 seconds for responses, ...
        raise_no_response=False,  # ... then check for response.empty instead of raising
        min_wait_consecutive=2.0,  # Wait at least 2 seconds to collect more than one message
        global_action_delay=1.8,  # Space out all messages by 1.8 seconds
        workdir=examples_dir,
        config_file=str(examples_dir / 'config.ini')
    )

    print("Starting integration test service...")
    c.start()
    print("Client ready.")

    yield c  # py.test sugar to separate setup from teardown

    # Teardown
    c.stop()

