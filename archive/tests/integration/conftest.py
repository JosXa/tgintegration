from pathlib import Path

import pytest
from decouple import config

examples_dir = Path(__file__).parent.parent.parent / "examples"


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
