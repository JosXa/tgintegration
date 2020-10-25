import asyncio
import re
from typing import List
from unittest.mock import Mock

from decouple import config
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.types import SentCode

from tgintegration import BotController
from tgintegration.collector import collect
from tgintegration.collector import Expectation
from tgintegration.collector import TimeoutSettings

clients: List[Client] = []


async def create_session_string(test_mode: bool = False):
    memory_client = Client(
        session_name=":memory:",
        api_id=config("API_ID"),
        api_hash=config("API_HASH"),
        test_mode=test_mode,
        phone_number=config("TEST_AGENT_PHONE"),
    )

    if len(clients) == 0:
        await memory_client.start()
        result = await memory_client.export_session_string()
    else:
        intercept_client = clients[0]

        async def tg_service_notifications_filter(_, __, m: Message):
            print(m)
            return bool(m.from_user and m.from_user.first_name == "Telegram")

        # TODO: Use standalone `collect` (https://github.com/JosXa/tgintegration/issues/19)
        controller = Mock(BotController)
        controller.configure_mock(client=intercept_client)

        # noinspection PydanticTypeChecker
        async with collect(
            controller,
            tg_service_notifications_filter,
            expectation=Expectation(min_messages=1, max_messages=1),
            timeouts=TimeoutSettings(max_wait=120),
        ) as res:
            sent_code = await initiate_send_code(memory_client)

        code = re.findall(r".*([0-9]{5}).*", res.full_text, re.DOTALL)[0]

        await memory_client.sign_in(
            memory_client.phone_number, sent_code.phone_code_hash, code
        )
        result = await memory_client.export_session_string()

    if len(clients) >= 1:
        await memory_client.stop()

    clients.append(memory_client)
    return result


async def initiate_send_code(client: Client) -> SentCode:
    is_authorized = await client.connect()
    assert not is_authorized

    await client.authorize()
    sent_code = await client.send_code(client.phone_number)
    assert sent_code.type == "app"

    return sent_code


if __name__ == "__main__":
    N = 2
    TEST_MODE = False

    strings = []

    try:
        for _ in range(N):
            strings.append(asyncio.run(create_session_string(test_mode=TEST_MODE)))
    finally:
        print(
            f"\n============ {len(strings)}/{N} session strings created: ============"
        )
        for s in strings:
            print(s)
