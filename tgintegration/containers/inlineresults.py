import re
from operator import attrgetter
from typing import List

from pyrogram.api.types import BotInlineResult


class InlineResult:
    def __init__(self, client, result, query_id):
        self._client = client
        self.result = result
        self.query_id = query_id

    def send(
            self,
            chat_id,
            disable_notification,
            reply_to_message_id
    ):
        return self._client.send_inline_bot_result(
            chat_id,
            self.query_id,
            self.result.id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id
        )

    def send_await(
            self,
            chat_id,
            filters=None,
            num_expected=None,
            disable_notification=None,
            reply_to_message_id=None,
            raise_=None
    ):
        return self._client.send_inline_bot_result_await(
            chat_id,
            query_id=self.query_id,
            result_id=self.result.id,
            filters=filters,
            num_expected=num_expected,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            raise_=raise_
        )

    @property
    def id(self):
        return self.result.id

    @property
    def full_text(self):
        return "{}\n{}".format(self.result.title, self.result.description)

    def __str__(self):
        return str(self.result)

    def __hash__(self):
        return hash(self.result.id)

    def __eq__(self, other):
        return self.id == other.id


class InlineResultContainer:
    def __init__(
            self,
            client,
            bot,
            query,
            bot_results,
            offset='',
            geo_point=None
    ):
        self._client = client
        self.bot = bot
        self.query = query
        self._bot_results = bot_results
        self.current_offset = offset
        self.geo_point = geo_point

    @property
    def results(self) -> List[BotInlineResult]:
        return self._bot_results.results

    @property
    def query_id(self):
        return self._bot_results.query_id

    @property
    def gallery(self):
        return self._bot_results.gallery

    def has_next_page(self):
        return bool(self._bot_results.next_offset)

    def load_next_page(self):
        if not self.has_next_page():
            return None
        if self.current_offset == self._bot_results.next_offset:
            return self

        return self._client.get_inline_bot_results(
            self.bot, self.query, self._bot_results.next_offset, self.geo_point
        )

    @property
    def can_switch_pm(self):
        return self._bot_results.switch_pm

    def switch_pm(self):
        if not self.can_switch_pm:
            raise AttributeError("This inline query does not allow switching to PM.")
        text = "/start {}".format(self._bot_results.switch_pm.start_param or '').strip()
        self._client.send_message(self.bot, text)

    def _match(self, pattern, getter):
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
            url_pattern=None
    ):

        # TODO:
        # article_types: List[str] = None,

        d = {
            title_pattern: attrgetter('title'),
            description_pattern: attrgetter('description'),
            message_pattern: attrgetter('send_message.message'),
            url_pattern: attrgetter('url')
        }

        results = set()
        for item in d.items():
            matches = self._match(*item)
            for r in matches:
                results.add(
                    InlineResult(self._client, r, self.query_id)
                )

        return results
