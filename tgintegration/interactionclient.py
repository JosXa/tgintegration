import asyncio
import inspect
import logging
import time
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client, Filters, Message, MessageHandler
from pyrogram.api import types
from pyrogram.api.errors import FloodWait, RpcMcgetFail
from pyrogram.api.functions.messages import GetBotCallbackAnswer, GetInlineBotResults
from pyrogram.api.types import InputGeoPoint
from pyrogram.session import Session
# Do not show Pyrogram license
from tgintegration.awaitableaction import AwaitableAction
from tgintegration.containers.inline_results import InlineResults
from tgintegration.response import InvalidResponseError, Response

Session.notice_displayed = True


class InteractionClient(Client):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        super().__init__(*args, **kwargs)

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
            response.started = time.time()

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
            override_messages=None,
            max_wait_response=None,
            min_wait_consecutive=None
    ):
        """
        Send messages to a bot to determine whether it is online.

        Args:
            peer:
            override_messages:

        Returns:

        """
        # TODO: should this method also handle inline queries?

        messages = ["/start"]
        if override_messages:
            messages = override_messages

        def send_pings():
            for n, m in enumerate(messages):
                try:
                    if n >= 1:
                        time.sleep(1)
                    self.send_message(peer, m)
                except FloodWait as e:
                    if e.x > 5:
                        self.logger.warning("send_message flood: waiting {} seconds".format(e.x))
                    time.sleep(e.x)
                    continue

        action = AwaitableAction(
            send_pings,
            filters=Filters.chat(peer),
            max_wait=max_wait_response,
            min_wait_consecutive=min_wait_consecutive,
        )

        return self.act_await_response(action)

    def get_inline_bot_results(
            self,
            bot: int or str,
            query: str,
            offset: str = "",
            location_or_geo: Union[tuple, InputGeoPoint] = None
    ):
        if location_or_geo:
            if isinstance(location_or_geo, tuple):
                geo_point = InputGeoPoint(
                    lat=location_or_geo[0],
                    long=location_or_geo[1]
                )
            else:
                geo_point = location_or_geo
        else:
            geo_point = None

        request = self.send(
            GetInlineBotResults(
                bot=self.resolve_peer(bot),
                peer=types.InputPeerSelf(),
                query=query,
                offset=offset,
                geo_point=geo_point
            )
        )
        return InlineResults(self, bot, query, request, offset, geo_point=geo_point)

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

    def send_command(self, chat_id, command, params=None):
        """
        Send a slash-command with corresponding parameters.

        Args:
            command:

        Returns:

        """
        text = "/" + command.lstrip('/')
        if params:
            text += ' '
            text += ' '.join(params)

        return self.send_message(chat_id, text)


def __make_awaitable_method(class_, method_name, send_method):
    """
    Injects `*_await` version of a `send_*` method.
    """

    def f(
            self,
            *args,  # usually the chat_id and a string
            filters=None,
            num_expected=None,
            max_wait=15,
            min_wait_consecutive=2,
            **kwargs
    ):
        action = AwaitableAction(
            func=send_method,
            args=(self, *args),
            kwargs=kwargs,
            num_expected=num_expected,
            filters=filters,
            max_wait=max_wait,
            min_wait_consecutive=min_wait_consecutive
        )
        return self.act_await_response(action)

    method_name += '_await'
    f.__name__ = method_name

    setattr(class_, method_name, f)


for name, method in inspect.getmembers(InteractionClient, predicate=inspect.isfunction):
    if name.startswith('send_') and not name.endswith('_await'):
        __make_awaitable_method(InteractionClient, name, method)
