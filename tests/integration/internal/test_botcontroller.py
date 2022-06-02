import pytest

pytestmark = pytest.mark.asyncio


async def test_controller_me(controller):
    assert controller.me is not None

    expected = await controller.client.get_me()

    assert controller.me == expected
