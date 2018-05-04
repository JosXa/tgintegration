from tgintegration import IntegrationTestClient


def test_start(client: IntegrationTestClient):
    # Send /start and wait for 3 messages
    res = client.send_command_await("/start", num_expected=3)
    assert res.num_messages == 3
    assert res[0].sticker


def test_help(client: IntegrationTestClient):
    # Send /help and wait for one message
    res = client.send_command_await("/help", num_expected=1)

    # Make some assertions about the response
    assert 'reliable and unbiased bot catalog' in res.full_text.lower()
    kb = res[0].reply_markup.inline_keyboard
    assert len(kb[0]) == 3  # 3 buttons in first row
    assert len(kb[1]) == 1  # 1 button in second row

    # Click the inline button that says "Contributing"
    contributing = res.press_inline_button(pattern=r'.*Contributing')
    assert "to contribute to the botlist" in contributing.full_text.lower()

    # Click the inline button that says "Help"
    help_ = res.press_inline_button(pattern=r'.*Help')
    assert "first steps" in help_.full_text.lower()

    # Click the inline button that says "Examples"
    examples = res.press_inline_button(pattern=r'.*Examples')
    assert "examples for contributing to the botlist:" in examples.full_text.lower()
