import pytest

pytestmark = pytest.mark.asyncio


async def test_start(controller, client):
    async with controller.collect(count=3) as res:
        await controller.send_command("/start")

    assert res.num_messages == 3
    assert res[0].sticker  # First message is a sticker


async def test_ping(controller, client):
    assert await controller.ping_bot()


async def test_help(controller):
    # Send /help and wait for one message
    async with controller.collect(count=1) as res:
        await controller.send_command("/help")

    # Make some assertions about the response
    assert not res.empty, "Bot did not respond to /help command"
    assert "most reliable and unbiased bot catalog" in res.full_text.lower()
    keyboard = res.inline_keyboards[0]
    assert len(keyboard.rows[0]) == 3  # 3 buttons in first row
    assert len(keyboard.rows[1]) == 1  # 1 button in second row

    # Click the inline button that says "Contributing"
    contributing = await res.inline_keyboards[0].click(pattern=r".*Contributing")
    assert not contributing.empty, 'Pressing "Contributing" button had no effect.'
    assert "to contribute to the botlist" in contributing.full_text.lower()

    # Click the inline button that says "Help"
    help_ = await res.inline_keyboards[0].click(pattern=r".*Help")
    assert not contributing.empty, 'Pressing "Help" button had no effect.'
    assert "first steps" in help_.full_text.lower()

    # Click the inline button that says "Examples"
    examples = await res.inline_keyboards[0].click(pattern=r".*Examples")
    assert not examples.empty, 'Pressing "Examples" button had no effect.'
    assert "examples for contributing to the botlist:" in examples.full_text.lower()
