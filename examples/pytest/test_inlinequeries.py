import re

import pytest

from tgintegration import BotController


@pytest.fixture(scope="module")
def bots():
    return ["@bold", "@BotListBot", "@gif"]


@pytest.mark.asyncio
async def test_search(controller, client, bots):
    for username in bots:
        # First send the username in private chat to get target description of the peer_user
        async with controller.collect(count=1) as res:
            await client.send_message(controller.peer, username)

        assert not res.is_empty, "Bot did not yield a response for username {}.".format(
            username
        )
        full_expected = res.full_text

        res = await controller.query_inline(username)
        results = list(
            res.find_results(
                title_pattern=re.compile(r"{}\b.*".format(username), re.IGNORECASE)
            )
        )
        assert len(results) == 1, "Not exactly one result for {}".format(username)

        # Description of peer_user should be the same in inline query message and private message
        assert (
            full_expected in results[0].result.send_message.message
        ), "Message texts did not match."


@pytest.mark.asyncio
async def test_inline_queries(controller: BotController):
    test = ["contributing", "rules", "examples"]

    for t in test:
        res = await controller.query_inline(t)
        assert res.find_results(
            title_pattern=re.compile(r".*{}.*".format(t), re.IGNORECASE)
        ), "{} did not work".format(t)
