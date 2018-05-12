from tgintegration import BotIntegrationClient

from tgintegration import BotIntegrationClient

client = BotIntegrationClient(
    bot_under_test='@BotListBot',
    session_name='my_account',  # arbitrary file path to the Pyrogram session file
    api_id=API_ID,
    api_hash=API_HASH,
    max_wait_response=15,  # maximum timeout for bot responses
    min_wait_consecutive=2  # minimum time to wait for consecutive messages
)

client.start()
client.clear_chat()  # Let's start with a blank screen

response = client.send_command_await("start", num_expected=3)

assert len(response.messages) == 3

first_message = response.messages[0]
assert response.messages[0].sticker

second_message = response[1]

# Three buttons in the first row
assert len(second_message.reply_markup.inline_keyboard[0]) == 3

# Click the first button matching the pattern
examples = response.press_inline_button(pattern=r'.*Examples')

assert "Examples for contributing to the BotList" in examples.full_text
