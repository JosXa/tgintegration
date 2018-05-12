import re

import pytest

from tgintegration import BotIntegrationClient


@pytest.fixture(scope='module')
def bots():
    return ['@bold', '@BotListBot', '@ElectroEventsBot']


def test_search(client: BotIntegrationClient, bots):
    for username in bots:
        # First send the username in private chat to get target description of the bot
        res = client.send_message_await(username, num_expected=1)
        assert not res.empty, "Bot did not yield a response for username {}.".format(username)
        full_expected = res.full_text

        res = client.get_inline_bot_results(
            client.peer_id,
            username
        )
        results = res.find_results(
            title_pattern=re.compile(r'{}\b.*'.format(username), re.IGNORECASE)
        )
        assert len(results) == 1, "Not exactly one result for {}".format(username)

        # Description of bot should be the same in inline query message and private message
        assert full_expected in results.pop().result.send_message.message, \
            "Message texts did not match."


def test_other(client: BotIntegrationClient):
    test = ["contributing", "rules", "examples"]

    for t in test:
        res = client.get_inline_bot_results(client.peer_id, t)
        assert res.find_results(
            title_pattern=re.compile(r'.*{}.*'.format(t), re.IGNORECASE)
        ), "{} did not work".format(t)
