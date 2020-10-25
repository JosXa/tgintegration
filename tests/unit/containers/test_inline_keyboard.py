import inspect
from unittest.mock import Mock

import pytest
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton

from tgintegration import BotController
from tgintegration.containers import InlineKeyboard
from tgintegration.containers import NoButtonFound

BTN_A = InlineKeyboardButton("a", callback_data="a")
BTN_B = InlineKeyboardButton("b", callback_data="b")
BTN_C = InlineKeyboardButton("c", callback_data="c")


@pytest.mark.parametrize(
    "rows,idx,expected",
    [
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ]
            ],
            0,
            BTN_A,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ]
            ],
            1,
            BTN_B,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ]
            ],
            -1,
            BTN_B,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ]
            ],
            -2,
            BTN_A,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ]
            ],
            -3,
            NoButtonFound,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ],
                [BTN_C],
            ],
            0,
            BTN_A,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ],
                [BTN_C],
            ],
            1,
            BTN_B,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ],
                [BTN_C],
            ],
            2,
            BTN_C,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ],
                [BTN_C],
            ],
            3,
            NoButtonFound,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ],
                [BTN_C],
            ],
            -1,
            BTN_C,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ],
                [BTN_C],
            ],
            -2,
            BTN_B,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ],
                [BTN_C],
            ],
            -3,
            BTN_A,
        ),
        pytest.param(
            [
                [
                    BTN_A,
                    BTN_B,
                ],
                [BTN_C],
            ],
            -4,
            NoButtonFound,
        ),
    ],
)
def test_click_inline_keyboard_button_by_index(rows, idx, expected):
    """ https://github.com/JosXa/tgintegration/issues/2 """

    CHAT_ID = 12345
    MESSAGE_ID = 123
    client = Mock(Client)
    controller = Mock(BotController)
    controller.configure_mock(client=client)
    kb = InlineKeyboard(
        controller, chat_id=CHAT_ID, message_id=MESSAGE_ID, button_rows=rows
    )

    if inspect.isclass(expected) and issubclass(expected, Exception):
        with pytest.raises(expected):
            kb.find_button(index=idx)
    else:
        res = kb.find_button(index=idx)
        assert res == expected
