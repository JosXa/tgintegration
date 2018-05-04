from tgintegration import IntegrationTestClient


def test_explore_button(client: IntegrationTestClient):
    # Send /start to bot and wait for 3 messages
    res = client.send_command_await("/start", num_expected=3)

    # Extract keyboard button that says "Explore"
    btn = next(x for x in res.keyboard_buttons if 'explore' in x.lower())

    # Click the "Explore" keyboard button
    explore = client.send_message_await(btn)
    assert explore.num_messages == 1

    # Click the "Explore" inline keyboard button 10 times or until it says that all bots have been explored
    count = 10
    while "explored all the bots" not in explore.full_text:
        if count == 0:
            break  # ok

        # Pressing an inline button also makes the IntegrationTestClient listen for edit events.
        # As this would raise an error if the bot did not edit the message, this is a valid test case
        explore = explore.press_inline_button(r'.*🔄')  # emoji
        count -= 1


