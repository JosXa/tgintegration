import asyncio

from pyrogram import Filters

from tgintegration import BotController, InteractionClient, Response

# This example uses the configuration of `config.ini` (see examples/README)
client = InteractionClient(
    session_name="tgintegration_examples"  # Arbitrary file path to the Pyrogram session file
)

controller = BotController(bot_under_test="@BotListBot", client=client)


async def main():
    with client.collect(filters=Filters.text) as collection:
        await client.send_message("@botlistbot", "/start")
        await client.send_message("@botlistbot", "/help")
        response: Response = collection.expect(count=1, max_wait=5)
        assert response.full_text == "something something"

    with client.expect(count=1, max_wait=5, filters=Filters.text) as response:
        await client.send_message("@botlistbot", "/start")
        await client.send_message("@botlistbot", "/help")



if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
