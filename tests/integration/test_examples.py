from pathlib import Path

import pytest
from decouple import config


pytestmark = pytest.mark.asyncio
examples_dir = Path(__file__).parent.parent.parent / "examples"


# region Fixtures


# noinspection PyCallingNonCallable
@pytest.fixture(scope="session", autouse=True)
def generate_config_ini():
    lines = [
        "[pyrogram]",
        f'api_id={config("API_ID")}',
        f'api_hash={config("API_HASH")}',
    ]

    with open(examples_dir / "config.ini", "w+") as text_file:
        text_file.write("\n".join(lines))


@pytest.fixture(scope="session")
def session_name():
    # noinspection PyCallingNonCallable
    return config("SESSION_STRING")


# endregion


async def test_dinopark_example(session_name):
    # Late import so that the autouse fixtures run first
    from examples.automation import dinoparkbot

    client = dinoparkbot.create_client(session_name)
    game = dinoparkbot.create_game_controller(client)
    await game.perform_full_run()


async def test_idletown_example(session_name):
    # Late import so that the autouse fixtures run first
    from examples.automation import idletown

    idletown.MAX_RUNS = 1
    client = idletown.create_client(session_name)
    controller = idletown.create_game_controller(client)
    await idletown.perform_full_run(controller)


async def test_readme_example(session_name):
    # Late import so that the autouse fixtures run first
    from examples.automation import idletown

    idletown.MAX_RUNS = 1
    client = idletown.create_client(session_name)
    controller = idletown.create_game_controller(client)
    await idletown.perform_full_run(controller)
