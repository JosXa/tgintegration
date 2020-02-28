import re
from operator import attrgetter
from typing import *

from pyrogram import Client
from pyrogram.api.types import BotInlineResult
from pyrogram.api.types import InputGeoPoint, Message
from pyrogram.api.types.messages import BotResults
from pyrogram.client.filters.filter import Filter

from tgintegration import InteractionClient


class InlineResult:
    client: InteractionClient
    result: BotInlineResult
    query_id: int

    def __init__(
        self, client: 'InteractionClient', result: BotInlineResult, query_id: int
    ):
        pass

    def send_await(
        self,
        chat_id: Union[int, str],
        filters: Optional[Filter] = None,
        num_expected: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        raise_: Optional[bool] = None,
    ):
        pass

    @property
    def id(self) -> Any:
        pass

    @property
    def full_text(self) -> str:
        pass

    def __str__(self) -> str:
        pass

    def __hash__(self):
        pass

    def __eq__(self, other) -> bool:
        pass


class InlineResultContainer:
    def __init__(
        self,
        service: InteractionClient,
        bot: Union[int, str],
        query: str,
        bot_results: BotResults,
        offset: str = "",
        geo_point: Optional[InputGeoPoint] = None,
    ):
        pass

    @property
    def results(self) -> List[BotInlineResult]:
        pass

    @property
    def query_id(self) -> int:
        pass

    @property
    def gallery(self) -> bool:
        pass

    def has_next_page(self) -> bool:
        pass

    def load_next_page(self) -> Optional["InlineResultContainer"]:
        pass

    @property
    def can_switch_pm(self) -> bool:
        pass

    def switch_pm(self) -> Message:
        pass

    def _match(self, pattern, getter) -> List:
        pass

    def find_results(
        self,
        title_pattern=None,
        description_pattern=None,
        message_pattern=None,
        url_pattern=None,
    ) -> Set[InlineResult]:
        pass
