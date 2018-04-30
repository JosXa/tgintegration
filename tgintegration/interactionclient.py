import asyncio
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Pattern, Set
from pyrogram import Client, Filters, MessageHandler
from pyrogram.api.errors import FloodWait, RpcMcgetFail
from pyrogram.api.functions.messages import GetBotCallbackAnswer
from pyrogram import Message
from pyrogram.session import Session

# Do not show Pyrogram license
Session.notice_displayed = True


class AwaitableAction:
    """
    Represents an action to be sent by the client while waiting for a response by the peer.
    """

    def __init__(
            self,
            func: Callable,
            args: List = None,
            kwargs: Dict = None,
            filters: Filters = None,
            num_expected: int = None,
            max_wait: int = 20,
            min_wait_consecutive: int = None,
    ):
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.filters = filters
        self._num_expected = num_expected
        self.consecutive_wait = max(0, min_wait_consecutive) if min_wait_consecutive else 0
        self.max_wait = max_wait

    @property
    def num_expected(self):
        return self._num_expected

    @num_expected.setter
    def num_expected(self, value):
        if value is not None:
            if not isinstance(value, int) or value < 1:
                raise ValueError("`num_expected` must be an int and greater or equal 1")
            if value > 1 and not self.consecutive_wait:
                raise ValueError("If the number of expected messages greater than one, "
                                 "`min_wait_consecutive` must be given.")
        self._num_expected = value


class Response:
    def __init__(self, client: 'InteractionClient', to_action: AwaitableAction):
        self.client = client
        self.action = to_action
        self.action_result = None
        self._messages = []  # type: List[Message]

    @property
    def messages(self) -> List[Message]:
        return self._messages

    def _add_message(self, message: Message):
        self._messages.append(message)

    @property
    def empty(self) -> bool:
        return not self._messages

    @property
    def num_messages(self) -> int:
        return len(self._messages)

    @property
    def full_text(self):
        return '\n'.join(x.text for x in self._messages if x.text) or ''

    def click_inline_button(self, pattern: Pattern):
        pattern = re.compile(pattern)
        for m in self._messages:
            markup = m.reply_markup
            if markup and hasattr(markup, 'inline_keyboard'):
                for row in markup.inline_keyboard:
                    for button in row:
                        if pattern.match(button.text):
                            chat_id = m.chat.id

                            action = AwaitableAction(
                                func=self.client.press_inline_button,
                                args=(chat_id, m, bytes(button.callback_data, "utf-8")),
                                filters=Filters.chat(chat_id),
                                max_wait=10,
                                min_wait_consecutive=3
                            )
                            return self.client.act_await_response(action)
        raise ValueError("No button found.")

    @property
    def keyboard_buttons(self) -> Set[str]:
        all_buttons = set()
        for m in self._messages:
            markup = m.reply_markup
            if markup and hasattr(markup, 'keyboard'):
                for row in markup.keyboard:
                    for button in row:
                        all_buttons.add(button)
        return all_buttons

    @property
    def last_message_timestamp(self) -> datetime:
        if self.empty:
            return None
        # TODO: Dan should fix this
        return datetime.fromtimestamp(self._messages[-1].date)

    def __getitem__(self, item):
        return self._messages[item]

    def __str__(self):
        if self.empty:
            return "Empty response"
        return '\nthen\n'.join(['"{}"'.format(m.text) for m in self._messages])


class InvalidResponseError(Exception):
    pass


class InteractionClient(Client):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        super(InteractionClient, self).__init__(*args, **kwargs)

    def act_await_response(self, action: AwaitableAction) -> Response:
        response = Response(self, action)

        def collect(_, message):
            # noinspection PyProtectedMember
            response._add_message(message)

        handler, group = self.add_handler(
            MessageHandler(
                collect,
                filters=action.filters
            ), -1)

        try:
            response.action_result = action.func(*action.args, **action.kwargs)

            timeout_end = datetime.now() + timedelta(seconds=action.max_wait)

            while response.empty:
                if datetime.now() > timeout_end:
                    return response
                asyncio.sleep(0.3)

            if action.consecutive_wait:
                consecutive_delta = timedelta(seconds=action.consecutive_wait)

                # A response was received
                # Wait for consecutive messages from the peer
                while True:
                    now = datetime.now()

                    if action.num_expected:
                        if response.num_messages < action.num_expected:
                            if now > timeout_end:
                                raise InvalidResponseError(
                                    "Expected {} messages but only received {} after waiting {} "
                                    "seconds.".format(
                                        action.num_expected,
                                        response.num_messages,
                                        action.max_wait
                                    ))
                        elif response.num_messages > action.num_expected:
                            raise InvalidResponseError(
                                "Expected {} messages but received {}.".format(
                                    action.num_expected,
                                    response.num_messages
                                ))
                        else:
                            return response
                    else:
                        if (
                                now > response.last_message_timestamp + consecutive_delta
                                or now > timeout_end
                        ):
                            return response

                    asyncio.sleep(0.3)

            return response
        except RpcMcgetFail as e:
            self.logger.info(e)
            time.sleep(60)  # Internal Telegram error
        finally:
            self.remove_handler(handler, group)

    def ping_bot(
            self,
            peer,
            timeout=15,
            override_messages: List[str] = None,
            inline_queries: List[str] = None
    ) -> Response:
        messages = ["/start"]
        if override_messages:
            messages = override_messages

        def send_pings():
            for n, m in enumerate(messages):
                try:
                    if n >= 1:
                        asyncio.sleep(1)
                    self.send_message(peer, m)
                except FloodWait as e:
                    if e.x > 5:
                        self.logger.warning("send_message flood: waiting {} seconds".format(e.x))
                    time.sleep(e.x)  # not asyncio.sleep, rather stop the whole thread
                    continue

        action = AwaitableAction(
            send_pings,
            filters=Filters.chat(peer),
            max_wait=timeout,
            min_wait_consecutive=2,
        )

        message_response = self.act_await_response(action)

        if message_response:
            return message_response

        if inline_queries:
            for q in inline_queries:
                res = self.get_inline_bot_results(peer, q)
                print(res)

    def remove_handler(self, handler, group: int = 0):
        # TODO: Waiting - Let Dan implement this
        if group not in self.dispatcher.groups:
            raise ValueError("Wrong group you sucker")

        self.dispatcher.groups[group].remove(handler)

    def add_handler(self, handler, group: int = 0):
        super().add_handler(handler, group)
        return handler, group

    def press_inline_button(self, user_id, on_message, callback_data):
        if isinstance(on_message, Message):
            mid = on_message.message_id
        elif isinstance(on_message, int):
            mid = on_message
        else:
            raise ValueError("Invalid argument `on_message`")

        return self.send(
            GetBotCallbackAnswer(
                peer=self.resolve_peer(user_id),
                msg_id=mid,
                data=callback_data
            )
        )
