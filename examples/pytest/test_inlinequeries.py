import re

import pytest

from tgintegration import BotController
from tgintegration import Response

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
def bots():
    return ["@bold", "@BotListBot", "@gif"]


async def test_search(controller, client, bots):
    for username in bots:
        # First send the username in private chat to get target description of the peer_user
        async with controller.collect(count=1) as res:  # type: Response
            await client.send_message(controller.peer, username)

        assert not res.is_empty, "Bot did not yield a response for username {}.".format(
            username
        )
        full_expected = res.full_text

        inline_response = await controller.query_inline(username)
        results = list(
            inline_response.find_results(
                title_pattern=re.compile(r"{}\b.*".format(username), re.IGNORECASE)
            )
        )
        assert len(results) == 1, "Not exactly one result for {}".format(username)

        # Description of peer_user should be the same in inline query message and private message
        assert (
            full_expected in results[0].result.send_message.message
        ), "Message texts did not match."


@pytest.mark.parametrize("test_input", ["contributing", "rules", "examples"])
async def test_inline_queries(controller: BotController, test_input: str):
    inline_results = await controller.query_inline(test_input)
    single_result = inline_results.find_results(
        title_pattern=re.compile(r".*{}.*".format(test_input), re.IGNORECASE)
    )
    assert len(single_result) == 1, "{} did not work".format(test_input)
