"""
Full version of the GitHub README.
"""
import asyncio
from tgintegration import BotController, InteractionClient

print("Initializing service...")
# This example uses the configuration of `config.ini` (see examples/README)
client = InteractionClient(
    session_name="tgintegration_examples"  # Arbitrary file path to the Pyrogram session file
)

controller = BotController(
    bot_under_test="@BotListBot",
    client=client,
    max_wait_response=8,  # Maximum timeout for bot responses
    min_wait_consecutive=2,  # Minimum time to wait for consecutive messages
    raise_no_response=True,  # Raise `InvalidResponseError` when no response received
)


async def run_example():

    print("Starting...")
    await controller.start()

    print("Clearing chat to start with a blank screen...")
    await controller.clear_chat()

    print(
        "Send the /start command to the bot_under_test and 'await' exactly three messages..."
    )
    async with controller.collect() as collector:
        await controller.send_command("start")

        response = await collector.expect(count=3)

        assert response.num_messages == 3
        print("Three messages received.")
        assert response.messages[0].sticker
        print("First message is a sticker.")

        print("Let's examine the buttons in the response...")
        inline_keyboard = response.inline_keyboards[0]
        assert len(inline_keyboard.rows[0]) == 3
        print("There are three buttons in the first row.")

        # We can also query and press the inline keyboard buttons:
        print("Click the first button matching the pattern r'.*Examples'")
        examples = await response.inline_keyboards[0].press_button_await(
            pattern=r".*Examples"
        )

    assert "Examples for contributing to the BotList" in examples.full_text
    # As the bot edits the message, `press_inline_button` automatically listens for `MessageEdited`
    # events and picks up on the edit, returning it as `Response`.

    print("So what happens when we send an invalid query or the bot fails to respond?")
    from tgintegration import InvalidResponseError

    try:
        # The following instruction will raise an `InvalidResponseError` after
        # `service.max_wait_response` seconds. This is because we passed `raise_no_response = True`
        # in the service initialization.
        print("Expecting undefined command to raise InvalidResponseError...")
        await controller.send_command_await("ayylmao", raise_=True)
    except InvalidResponseError:
        print("Raised.")  # Ok

    # The `InteractionClient` is based off a regular Pyrogram client, meaning that, in addition to
    #  the `send_*_await` methods, all normal Pyro methods still work:
    print("Calling a normal `send_message` method...")
    await client.send_message(
        controller.bot_under_test, "Hello from Pyrogram"
    )  # Not waiting for response

    # `send_*_await` methods automatically use the `bot_under_test` as peer:
    res = await controller.send_message_await(
        "Hello from TgIntegration", max_wait=2, raise_=False
    )
    # If `raise_` is explicitly set to False, no exception is raised:
    assert res.empty
    # Note that when no response is expected and no validation thereof is necessary, ...
    await controller.send_photo_await("_assets/photo.jpg", max_wait=0, raise_=False)
    await controller.send_voice_await("_assets/voice.ogg", max_wait=0, raise_=False)
    # ... it makes more sense to use the "unawaitable" methods:
    await controller.client.send_photo(controller.bot_under_test, "_assets/photo.jpg")
    await controller.client.send_voice(controller.bot_under_test, "_assets/voice.ogg")

    # Custom awaitable Actions
    from tgintegration import AwaitableAction, Response
    from pyrogram import Filters

    peer = "@BotListBot"

    print("Constructing custom `AwaitableAction` object...")
    action = AwaitableAction(
        func=client.send_message,
        kwargs=dict(chat_id=peer, text="🔄 Explore"),
        num_expected=1,
        # Wait for messages only by the peer we're interacting with
        filters=Filters.user(peer) & Filters.incoming,
        # Time out and raise after 15 seconds
        max_wait=15,
    )

    print("Executing `AwaitableAction`...")
    response = await client.act_await_response(action)  # type: Response
    print("Done.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_example())
