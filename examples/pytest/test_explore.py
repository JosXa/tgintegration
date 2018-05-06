from tgintegration import BotIntegrationClient


def test_explore_button(client: BotIntegrationClient):
    # Send /start to bot and wait for 3 messages
    start = client.send_command_await("/start", num_expected=3)

    # Click the "Explore" keyboard button
    explore = start.reply_keyboard.press_button_await(pattern=r'.*Explore')

    assert explore.num_messages == 1
    assert explore.inline_keyboards

    # Click the "Explore" inline keyboard button 10 times or until it says that all bots have been explored
    count = 10
    while "explored all the bots" not in explore.full_text:
        if count == 0:
            break  # ok

        # Pressing an inline button also makes the BotIntegrationClient listen for edit events.
        # As this would raise an error if the bot did not edit the message, this is a valid test case
        explore = explore.inline_keyboards[0].press_button_await(index=2)
        count -= 1


