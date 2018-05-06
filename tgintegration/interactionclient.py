import inspect
import logging
import time
from datetime import datetime, timedelta

from pyrogram import Client, Filters, Message, MessageHandler
from pyrogram.api import types
from pyrogram.api.errors import FloodWait, RpcMcgetFail
from pyrogram.api.functions.messages import GetBotCallbackAnswer, GetInlineBotResults
from pyrogram.api.types import InputGeoPoint
from pyrogram.session import Session
from .awaitableaction import AwaitableAction
from .containers import InlineResultContainer
from .response import InvalidResponseError, Response

# Do not show Pyrogram license
Session.notice_displayed = True


class InteractionClient(Client):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        super().__init__(*args, **kwargs)

    def act_await_response(self, action, raise_=True):
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

            # print(action.args, action.kwargs)
            response.action_result = action.func(*action.args, **action.kwargs)

            timeout_end = datetime.now() + timedelta(seconds=action.max_wait)

            while response.empty:
                if time.time() - response.started > 5:
                    self.logger.debug("No response received yet after 5 seconds")
                if datetime.now() > timeout_end:
                    self.logger.debug("Aborting as no response was received after {} seconds.".format(action.max_wait))
                    return response
                time.sleep(0.3)

            if action.consecutive_wait:
                consecutive_delta = timedelta(seconds=action.consecutive_wait)

                # A response was received
                # Wait for consecutive messages from the peer
                while True:
                    now = datetime.now()

                    if action.num_expected:
                        if response.num_messages < action.num_expected:
                            if now > timeout_end:
                                msg = "Expected {} messages but only received {} after waiting {} "
                                "seconds.".format(
                                    action.num_expected,
                                    response.num_messages,
                                    action.max_wait
                                )

                                if raise_:
                                    raise InvalidResponseError(msg)
                                else:
                                    self.logger.debug(msg)
                                    return False

                        elif response.num_messages > action.num_expected:
                            msg = "Expected {} messages but received {}.".format(
                                action.num_expected,
                                response.num_messages
                            )

                            if raise_:
                                raise InvalidResponseError(msg)
                            else:
                                self.logger.debug(msg)
                                return False
                        else:
                            return response
                    else:
                        if (
                                now > response.last_message_timestamp + consecutive_delta
                                or now > timeout_end
                        ):
                            return response

                    time.sleep(0.2)

            return response
        except RpcMcgetFail as e:
            self.logger.warning(e)
            time.sleep(60)  # Internal Telegram error
        finally:
            self.remove_handler(handler, group)

    def ping_bot(
            self,
            bot,
            override_messages=None,
            max_wait_response=None,
            min_wait_consecutive=None
    ):
        messages = ["/start"]
        if override_messages:
            messages = override_messages

        def send_pings():
            for n, m in enumerate(messages):
                try:
                    if n >= 1:
                        time.sleep(1)
                    self.send_message(bot, m)
                except FloodWait as e:
                    if e.x > 5:
                        self.logger.warning("send_message flood: waiting {} seconds".format(e.x))
                    time.sleep(e.x)
                    continue

        action = AwaitableAction(
            send_pings,
            filters=Filters.chat(bot),
            max_wait=max_wait_response,
            min_wait_consecutive=min_wait_consecutive,
        )

        return self.act_await_response(action)

    def get_inline_bot_results(
            self,
            bot,
            query,
            offset,
            location_or_geo=None
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
        return InlineResultContainer(self, bot, query, request, offset, geo_point=geo_point)

    def press_inline_button(self, chat_id, on_message, callback_data, retries=0):
        if isinstance(on_message, Message):
            mid = on_message.message_id
        elif isinstance(on_message, int):
            mid = on_message
        else:
            raise ValueError("Invalid argument `on_message`")

        request = GetBotCallbackAnswer(
            peer=self.resolve_peer(chat_id),
            msg_id=mid,
            data=bytes(callback_data, 'utf-8')
        )

        if retries > 0:
            return self.session.send(request, retries=retries)
        else:
            # noinspection PyProtectedMember
            self.session._send(request, wait_response=False)
            return True

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
            raise_=True,
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
        return self.act_await_response(action, raise_=raise_)

    method_name += '_await'
    f.__name__ = method_name

    setattr(class_, method_name, f)


for name, method in inspect.getmembers(InteractionClient, predicate=inspect.isfunction):
    if name.startswith('send_') and not name.endswith('_await'):
        __make_awaitable_method(InteractionClient, name, method)
