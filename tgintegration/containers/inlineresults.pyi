from typing import Any, Callable, List, Pattern, Set, Union

from pyrogram.api.types import BotInlineResult, InputGeoPoint, Message
from pyrogram.api.types.messages import BotResults
from pyrogram.client.filters.filter import Filter
from tgintegration import InteractionClient, Response


class InlineResult:
    result: BotInlineResult
    query_id: int

    _client: InteractionClient

    def __init__(self, client: InteractionClient, result: BotInlineResult, query_id: int):
        ...

    def send(
            self,
            chat_id: Union[int, str],
            disable_notification: bool = None,
            reply_to_message_id: int = None
    ) -> Message:
        ...

    def send_await(
            self,
            chat_id: Union[int, str],
            filters: Filter = None,
            num_expected: int = None,
            disable_notification: bool = None,
            reply_to_message_id: int = None
    ) -> Response:
        ...

    def id(self) -> Any: ...

    def __str__(self) -> str: ...

    def __hash__(self) -> Any: ...

    def __eq__(self, other: Any) -> bool: ...


class InlineResultContainer:
    bot: Union[int, str]
    query: str
    current_offset: str
    geo_point: Union[InputGeoPoint, None]

    _client: InteractionClient
    _bot_results: BotResults

    def __init__(
            self,
            client: InteractionClient,
            bot: Union[int, str],
            query: str,
            bot_results: BotResults,
            offset: str = ...,
            geo_point: InputGeoPoint = None
    ):
        ...

    def results(self) -> List[BotInlineResult]:
        ...

    def query_id(self) -> str:
        ...

    def gallery(self) -> Any:  # TODO: return type
        ...

    def has_next_page(self) -> bool:
        ...

    def load_next_page(self) -> Union[InlineResultContainer, None]:
        ...

    def can_switch_pm(self) -> bool:
        ...

    def switch_pm(self) -> Message:
        ...

    def _match(self, pattern: Pattern, getter: Callable) -> List:
        ...

    def find_results(
            self,
            title_pattern: Pattern = None,
            description_pattern: Pattern = None,
            message_pattern: Pattern = None,
            url_pattern: Pattern = None
    ) -> Set[InlineResult]:
        ...
