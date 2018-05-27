import asyncio
import base64
import inspect
import json
import logging
import os
import time
from datetime import datetime, timedelta

from pyrogram import Client, Filters, Message, MessageHandler
from pyrogram.api import types
from pyrogram.api.errors import FloodWait, RpcMcgetFail
from pyrogram.api.functions.messages import GetBotCallbackAnswer, GetInlineBotResults
from pyrogram.api.functions.users import GetUsers
from pyrogram.api.types import InputGeoPoint
from pyrogram.session import Session

from .awaitableaction import AwaitableAction
from .containers import InlineResultContainer
from .response import InvalidResponseError, Response

# Do not show Pyrogram license
Session.notice_displayed = True

SLEEP_DURATION = 0.15


class InteractionClientAsync(Client):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        super().__init__(*args, **kwargs)

    async def act_await_response(self, action, raise_=True):
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
            # Start timer
            response.started = time.time()

            # Execute the action
            response.action_result = await asyncio.ensure_future(
                action.func(*action.args, **action.kwargs)
            )

            # Calculate maximum wait time
            timeout_end = datetime.now() + timedelta(seconds=action.max_wait)

            # Wait for the first reply
            while response.empty:

                if time.time() - response.started > 5:
                    self.logger.debug("No response received yet after 5 seconds")

                if datetime.now() > timeout_end:
                    msg = "Aborting because no response was received after {} seconds.".format(
                        action.max_wait)

                    if raise_:
                        raise InvalidResponseError(msg)
                    else:
                        self.logger.debug(msg)

                    return response

                await asyncio.sleep(SLEEP_DURATION)

            # A response was received
            if action.consecutive_wait:
                # Wait for more consecutive messages from the peer
                consecutive_delta = timedelta(seconds=action.consecutive_wait)

                while True:
                    now = datetime.now()

                    if action.num_expected is not None:
                        # User has set explicit number of messages to await
                        if response.num_messages < action.num_expected:
                            # Less messages than expected (so far)
                            if now > timeout_end:
                                # Timed out
                                msg = "Expected {} messages but only received {} after waiting {} "
                                "seconds.".format(
                                    action.num_expected,
                                    response.num_messages,
                                    action.max_wait
                                )

                                if raise_:  # TODO: should this really be toggleable? raise always?
                                    raise InvalidResponseError(msg)
                                else:
                                    self.logger.debug(msg)
                                    return False
                            # else: continue

                        elif response.num_messages > action.num_expected:
                            # More messages than expected
                            msg = "Expected {} messages but received {}.".format(
                                action.num_expected,
                                response.num_messages
                            )

                            if raise_:  # TODO: should this really be toggleable? raise always?
                                raise InvalidResponseError(msg)
                            else:
                                self.logger.debug(msg)
                                return False
                        else:
                            return response
                    else:
                        # User has not provided an expected number of messages
                        if (
                                now > (response.last_message_timestamp + consecutive_delta)
                                or
                                now > timeout_end
                        ):
                            return response

                    await asyncio.sleep(SLEEP_DURATION)

            return response

        except RpcMcgetFail as e:
            self.logger.warning(e)
            time.sleep(60)  # Internal Telegram error
        finally:
            # Remove the one-off handler for this action
            self.remove_handler(handler, group)

    async def ping_bot(
            self,
            bot,
            override_messages=None,
            max_wait_response=None,
            min_wait_consecutive=None,
            raise_=True
    ):
        messages = ["/start"]
        if override_messages:
            messages = override_messages

        async def send_pings():
            for n, m in enumerate(messages):
                try:
                    if n >= 1:
                        await asyncio.sleep(1)
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

        return await self.act_await_response(action, raise_=raise_)

    def get_inline_bot_results(
            self,
            bot,
            query,
            offset='',
            latitude=None,
            longitude=None
    ):
        geo_point = InputGeoPoint(
            lat=latitude,
            long=longitude
        )

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

    def send_command(self, bot, command, params=None):
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

        return self.send_message(bot, text)

    def export_minimal_session_b64(self, filename, include_peers=None):
        auth_key = base64.b64encode(self.auth_key).decode()
        auth_key = [auth_key[i: i + 43] for i in range(0, len(auth_key), 43)]

        s = dict(
            dc_id=self.dc_id,
            test_mode=self.test_mode,
            auth_key=auth_key,
            user_id=self.user_id,
            date=self.date,
        )

        if include_peers:
            if not isinstance(include_peers, list):
                include_peers = [include_peers]

            peer_details = self.send(GetUsers([self.resolve_peer(x) for x in include_peers]))

            peers_by_id = {}
            peers_by_username = {}
            peers_by_phone = {}

            for peer in peer_details:
                peers_by_id[peer.id] = peer.access_hash
                if peer.username:
                    peers_by_username[peer.username.lower()] = peer.id
                if peer.phone:
                    peers_by_phone[peer.phone] = peer.id

            s.update(dict(
                peers_by_id=peers_by_id,
                peers_by_username=peers_by_username,
                peers_by_phone=peers_by_phone
            ))

        uglified_json = json.dumps(s, separators=(',', ':'))
        b64_encoded = base64.b64encode(bytes(uglified_json, 'utf-8')).decode()

        os.makedirs(self.workdir, exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(b64_encoded)
        return b64_encoded

    @classmethod
    def create_session_from_export(cls, encoded_bytes, output_session):
        decoded = base64.b64decode(encoded_bytes).decode()

        with open(output_session, "w", encoding="utf-8") as f:
            json.dump(json.loads(decoded), f, indent=4)


# region Dynamic code generation


def __make_awaitable_method(class_, method_name, send_method):
    """
    Injects `*_await` version of a `send_*` method.
    """

    # TODO: functools.wraps
    async def f(
            self,
            *args,  # usually the chat_id and a string (e.g. text, command, file_id)
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
        return await self.act_await_response(action, raise_=raise_)

    method_name += '_await'
    f.__name__ = method_name

    setattr(class_, method_name, f)


for name, method in inspect.getmembers(InteractionClientAsync, predicate=inspect.isfunction):
    if name.startswith('send_') and not name.endswith('_await'):
        __make_awaitable_method(InteractionClientAsync, name, method)

# endregion
