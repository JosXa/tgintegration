import pytest

from tgintegration import BotController, Response

pytestmark = pytest.mark.asyncio

# This example uses the configuration of `config.ini` (see examples/README)


@pytest.fixture(scope="function")
def controller(client):
    return BotController(client=client, peer="@BotListBot", max_wait_response=10.0, min_wait_consecutive=0.8)


async def test_new_syntax(controller, client):
    async with controller.collect(count=3, max_wait=10) as start_response:
        await client.send_message(controller.peer, "/start")

    assert start_response.num_messages == 3


    # async with controller.dialog() as dialog:
    #     response = dialog.send_command("/start")
    #     start_response = tgintegration.actors.collect(count=1)
    #
    # with controller.dialog(filters.text, max_wait=10) as dialog:
    #     await controller.send_message("@botlistbot", "/start")
    #     await controller.send_message("@botlistbot", "/help")
    #     response = tgintegration.actors.collect(count=2)
    #
    #     await controller.send_message("@botlistbot", "/help")
    #
    # with controller.dialog("@my_group_chat", filters.text, max_wait=10) as conversation:
    #     await controller.send_message("@my_group_chat", "/start@mybot")
    #     await controller.send_message("@my_group_chat", "/help@mybot")
    #     tgintegration.actors.collect(count=2)
    #
    # with controller.collect(count=1, max_wait=5, filters=filters.text) as response:
    #     await controller.send_message("@botlistbot", "/start")
    #     await controller.send_message("@botlistbot", "/help")
