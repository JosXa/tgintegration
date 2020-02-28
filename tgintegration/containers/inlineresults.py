import re
from operator import attrgetter
from typing import *

from pyrogram import Client
from pyrogram.api.types import BotInlineResult
from pyrogram.api.types import InputGeoPoint, Message
from pyrogram.api.types.messages import BotResults
from pyrogram.client.filters.filter import Filter

InteractionClient = TypeVar("InteractionClient")


class InlineResult:
    def __init__(
        self, client: "InteractionClient", result: BotInlineResult, query_id: int
    ):
        self._client = client
        self.result = result
        self.query_id = query_id

    def send(
        self,
        chat_id: Union[int, str],
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
    ):
        return self._client.send_inline_bot_result(
            chat_id,
            self.query_id,
            self.result.id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
        )

    def send_await(
        self,
        chat_id: Union[int, str],
        filters: Optional[Filter] = None,
        num_expected: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        raise_: Optional[bool] = None,
    ):
        return self._client.send_inline_bot_result_await(
            chat_id,
            query_id=self.query_id,
            result_id=self.result.id,
            filters=filters,
            num_expected=num_expected,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            raise_=raise_,
        )

    @property
    def id(self) -> Any:
        return self.result.id

    @property
    def full_text(self) -> str:
        return "{}\n{}".format(self.result.title, self.result.description)

    def __str__(self) -> str:
        return str(self.result)

    def __hash__(self):
        return hash(self.result.id)

    def __eq__(self, other) -> bool:
        return self.id == other.id


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
        self._client = service
        self.bot = bot
        self.query = query
        self._bot_results = bot_results
        self.current_offset = offset
        self.geo_point = geo_point

    @property
    def results(self) -> List[BotInlineResult]:
        return self._bot_results.results

    @property
    def query_id(self) -> int:
        return self._bot_results.query_id

    @property
    def gallery(self) -> bool:
        return self._bot_results.gallery

    def has_next_page(self) -> bool:
        return bool(self._bot_results.next_offset)

    def load_next_page(self) -> Optional["InlineResultContainer"]:
        if not self.has_next_page():
            return None
        if self.current_offset == self._bot_results.next_offset:
            return self

        return self._client.get_inline_bot_results(
            self.bot, self.query, self._bot_results.next_offset, self.geo_point
        )

    @property
    def can_switch_pm(self) -> bool:
        return self._bot_results.switch_pm

    def switch_pm(self) -> Message:
        if not self.can_switch_pm:
            raise AttributeError("This inline query does not allow switching to PM.")
        text = "/start {}".format(self._bot_results.switch_pm.start_param or "").strip()
        return self._client.send_message(self.bot, text)

    def _match(self, pattern, getter) -> List:
        results = []
        if pattern:
            compiled = re.compile(pattern)
            for result in self.results:
                compare = getter(result)
                if compiled.match(compare):
                    results.append(result)
        return results

    def find_results(
        self,
        title_pattern=None,
        description_pattern=None,
        message_pattern=None,
        url_pattern=None,
    ) -> Set[InlineResult]:

        # TODO:
        # article_types: List[str] = None,

        d = {
            title_pattern: attrgetter("title"),
            description_pattern: attrgetter("description"),
            message_pattern: attrgetter("send_message.message"),
            url_pattern: attrgetter("url"),
        }

        results = set()
        for item in d.items():
            matches = self._match(*item)
            for r in matches:
                results.add(InlineResult(self._client, r, self.query_id))

        return results
