import re
from operator import attrgetter
from typing import Any
from typing import List
from typing import Optional
from typing import Pattern
from typing import Set
from typing import TYPE_CHECKING
from typing import Union

from pyrogram.raw.types import BotInlineResult
from pyrogram.raw.types import InlineBotSwitchPM
from pyrogram.raw.types import WebDocument
from pyrogram.types import Message

from tgintegration.utils.iter_utils import flatten

if TYPE_CHECKING:
    from tgintegration.botcontroller import BotController

QueryId = str


class InlineResult:
    def __init__(
        self, controller: "BotController", result: BotInlineResult, query_id: int
    ):
        self._controller = controller
        self.result = result
        self._query_id = query_id

    def send(
        self,
        chat_id: Union[int, str],
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
    ):
        return self._controller.client.send_inline_bot_result(
            chat_id,
            self._query_id,
            self.result.id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
        )

    @property
    def id(self) -> Any:
        return self.result.id

    @property
    def full_text(self) -> str:
        return "{}\n{}".format(self.result.title, self.result.description)

    @property
    def title(self):
        return self.result.title

    @property
    def description(self):
        return self.result.description

    @property
    def url(self):
        return self.result.url

    @property
    def thumb(self) -> Optional[WebDocument]:
        return self.result.thumb

    @property
    def content(self) -> Optional[WebDocument]:
        return self.result.content

    def __str__(self) -> str:
        return str(self.result)

    def __hash__(self):
        return hash(self.result.id)

    def __eq__(self, other) -> bool:
        return self.id == other.id


class InlineResultContainer:
    def __init__(
        self,
        controller: "BotController",
        query: str,
        latitude: Optional[float],
        longitude: Optional[float],
        results: List[InlineResult],
        gallery: bool,
        switch_pm: InlineBotSwitchPM,
        users,
    ):
        self._controller = controller
        self.query = query
        self.latitude = latitude
        self.longitude = longitude
        self.results = results
        self.is_gallery = gallery
        self._switch_pm = switch_pm
        self._users = users

    @property
    def can_switch_pm(self) -> bool:
        return bool(self._switch_pm)

    async def switch_pm(self) -> Message:
        if not self.can_switch_pm:
            raise AttributeError("This inline query does not allow switching to PM.")
        text = "/start {}".format(self._switch_pm.start_param or "").strip()
        return await self._controller.client.send_message(
            self._controller.peer_id, text
        )

    def _match(self, pattern: Pattern, getter: attrgetter) -> List[InlineResult]:
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

        return set(flatten((self._match(*it) for it in d.items())))
