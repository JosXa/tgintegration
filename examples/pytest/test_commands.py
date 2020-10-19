import pytest

from tgintegration import BotController


@pytest.mark.asyncio
async def test_commands(controller: BotController):
    # The BotController automatically loads the available commands and we test them all here
    for c in controller.command_list:
        async with controller.collect() as res:
            await controller.send_command(c.command)
        assert not res.is_empty, "Bot did not respond to command /{}.".format(c.command)
