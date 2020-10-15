from collections import OrderedDict
from unittest.mock import Mock

import pytest
from pyrogram.dispatcher import Dispatcher

from tgintegration._handler_utils import find_free_group


@pytest.mark.parametrize(
    "group_indices,expected",
    [
        ([1, 2, 3], -1000),
        ([-1000], -1001),
        ([-999], -1000),
        ([-999, -1000, -1001], -1002),
        ([-1000, -1001, -1003], -1002),
    ],
)
def test_find_free_group(group_indices, expected):
    dp = Mock(Dispatcher)
    groups = OrderedDict({k: None for k in group_indices})
    dp.configure_mock(groups=groups)
    assert find_free_group(dp, -1000) == expected
