"""
Full version of the GitHub README.
"""
import asyncio
from pathlib import Path

from pyrogram import Client

from tgintegration import BotController
from tgintegration import Response

# This example uses the configuration of `config.ini` (see examples/README)
examples_dir = Path(__file__).parent.parent.absolute()
SESSION_NAME: str = "tgintegration_examples"


# This example uses the configuration of `config.ini` (see examples/README)
def create_client(session_name: str = SESSION_NAME) -> Client:
    client = Client(
        session_name=session_name,
        workdir=examples_dir,
        config_file=examples_dir / "config.ini",
    )
    client.load_config()
    return client


async def run_example(client: Client):
    controller = BotController(
        peer="@BotListBot",  # We are going to run tests on https://t.me/BotListBot
        client=client,
        max_wait=8,  # Maximum timeout for responses (optional)
        wait_consecutive=2,  # Minimum time to wait for more/consecutive messages (optional)
        raise_no_response=True,  # Raise `InvalidResponseError` when no response received (defaults to True)
        global_action_delay=2.5,  # Choosing a rather high delay so we can follow along in realtime (optional)
    )

    print("Clearing chat to start with a blank screen...")
    await controller.clear_chat()

    print("Sending /start and waiting for exactly 3 messages...")
    async with controller.collect(count=3) as response:  # type: Response
        await controller.send_command("start")

    assert response.num_messages == 3
    print("Three messages received, bundled as a `Response`.")
    assert response.messages[0].sticker
    print("First message is a sticker.")

    print("Let's examine the buttons in the response...")
    inline_keyboard = response.inline_keyboards[0]
    assert len(inline_keyboard.rows[0]) == 3
    print("Yep, there are three buttons in the first row.")

    # We can also press the inline keyboard buttons, in this case based on a pattern:
    print("Clicking the button matching the regex r'.*Examples'")
    examples = await inline_keyboard.click(pattern=r".*Examples")

    assert "Examples for contributing to the BotList" in examples.full_text
    # As the bot edits the message, `.click()` automatically listens for "message edited"
    # updates and returns the new state as `Response`.

    print("So what happens when we send an invalid query or the peer fails to respond?")
    from tgintegration import InvalidResponseError

    try:
        # The following instruction will raise an `InvalidResponseError` after
        # `controller.max_wait` seconds. This is because we passed `raise_no_response=True`
        # during controller initialization.
        print("Expecting unhandled command to raise InvalidResponseError...")
        async with controller.collect():
            await controller.send_command("ayylmao")
    except InvalidResponseError:
        print("Ok, raised as expected.")

    # If `raise_` is explicitly set to False, no exception is raised
    async with controller.collect(raise_=False) as response:  # type: Response
        print("Sending a message but expecting no reply...")
        await client.send_message(controller.peer_id, "Henlo Fren")

    # In this case, tgintegration will simply emit a warning, but you can still assert
    # that no response has been received by using the `is_empty` property.
    assert response.is_empty

    print("Success!")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_example(create_client()))
