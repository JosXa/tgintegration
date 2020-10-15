from unittest.mock import Mock

import pytest
from pyrogram.types import Message

from tgintegration.collector import Expectation


@pytest.mark.parametrize(
    "min_n,max_n,num_msgs,is_sufficient,is_match",
    [
        (1, 1, 0, False, False),
        (1, 1, 1, True, True),
        (1, 1, 2, False, False),
    ],
)
def test_expectation(
    min_n:int, max_n:int, num_msgs: int, is_sufficient: bool, is_match: bool
):
    obj = Expectation.from_min_max(min_n, max_n)
    msgs = [Mock(Message)] * num_msgs
    assert obj.is_sufficient(msgs) == is_sufficient
    assert obj._is_match(msgs) == is_match
