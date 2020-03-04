import asyncio
from typing import Union, List, Optional, Callable
from typing_extensions import Final

import inspect
import logging
import time
from datetime import datetime, timedelta
from pyrogram import Client, Filters, Message, MessageHandler
from pyrogram.api import types
from pyrogram.api.functions.messages import GetBotCallbackAnswer, GetInlineBotResults
from pyrogram.api.types import InputGeoPoint
from pyrogram.api.types import Message
from pyrogram.api.types.messages import BotCallbackAnswer
from pyrogram.client.filters.filter import Filter
from pyrogram.client.methods.messages.send_chat_action import ChatAction
from pyrogram.errors import RpcMcgetFail, FloodWait
from pyrogram.session import Session

from tgintegration.containers.response import InvalidResponseError, Response
from .awaitableaction import AwaitableAction
from .containers.inlineresults import InlineResultContainer

# Do not show Pyrogram license (we still ♡ you Dan)
Session.notice_displayed = True

SLEEP_DURATION: Final[float] = 0.15


class InteractionClient(Client):
    def __init__(self, *args, global_action_delay=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.global_action_delay = global_action_delay
        self._last_response = None

    async def act_await_response(
        self, action: AwaitableAction, raise_=True
    ) -> Optional[Response]:
        if self.global_action_delay and self._last_response:
            # Sleep for as long as the global delay prescribes
            sleep = self.global_action_delay - (
                time.time() - self._last_response.started
            )
            if sleep > 0:
                await asyncio.sleep(sleep)

        response = Response(self, action)

        async def collect(_, message):
            # noinspection PyProtectedMember
            response._add_message(message)

        # Add handler to empty group manually, as the Pyrogram lock seems to never release when trying
        # to use .add_handler
        group = -99  # TODO: find new, empty group
        if group not in self.dispatcher.groups:
            self.dispatcher.groups[group] = []
        handler = MessageHandler(callback=collect, filters=action.filters)
        self.dispatcher.groups[group].append(handler)

        try:
            # Start timer
            response.started = time.time()

            # Execute the action
            response.action_result = await action.func(*action.args, **action.kwargs)

            # Calculate maximum wait time
            timeout_end = datetime.now() + timedelta(seconds=action.max_wait)

            # Wait for the first reply
            while response.empty:

                if time.time() - response.started > 5:
                    self.logger.debug("No response received yet after 5 seconds")

                if datetime.now() > timeout_end:
                    msg = "Aborting because no response was received after {} seconds.".format(
                        action.max_wait
                    )

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
                                msg = (
                                    "Expected {} messages but only received {} "
                                    "after waiting {} seconds.".format(
                                        action.num_expected,
                                        response.num_messages,
                                        action.max_wait,
                                    )
                                )

                                if (
                                    raise_
                                ):  # TODO: should this really be toggleable? raise always?
                                    raise InvalidResponseError(msg)
                                else:
                                    self.logger.debug(msg)
                                    return None
                            # else: continue

                        elif response.num_messages > action.num_expected:
                            # More messages than expected
                            msg = "Expected {} messages but received {}.".format(
                                action.num_expected, response.num_messages
                            )

                            if (
                                raise_
                            ):  # TODO: should this really be toggleable? raise always?
                                raise InvalidResponseError(msg)
                            else:
                                self.logger.debug(msg)
                                return None
                        else:
                            self._last_response = response
                            return response
                    else:
                        # User has not provided an expected number of messages
                        if (
                            now > (response.last_message_timestamp + consecutive_delta)
                            or now > timeout_end
                        ):
                            self._last_response = response
                            return response

                    await asyncio.sleep(SLEEP_DURATION)

            self._last_response = response
            return response

        except RpcMcgetFail as e:
            self.logger.warning(e)
            await asyncio.sleep(60)  # Internal Telegram error
        finally:
            # Remove the one-off handler for this action
            self.remove_handler(handler, group)

    async def ping_bot(
        self,
        bot: Union[int, str],
        override_messages: List[str] = None,
        max_wait_response: float = None,
        min_wait_consecutive: float = None,
    ) -> Union[Response, bool]:
        messages = ["/start"]
        if override_messages:
            messages = override_messages

        async def send_pings():
            for n, m in enumerate(messages):
                try:
                    if n >= 1:
                        await asyncio.sleep(1)
                    await self.send_message(bot, m)
                except FloodWait as e:
                    if e.x > 5:
                        self.logger.warning(
                            "send_message flood: waiting {} seconds".format(e.x)
                        )
                    await asyncio.sleep(e.x)
                    continue

        action = AwaitableAction(
            send_pings,
            filters=Filters.chat(bot),
            max_wait=max_wait_response,
            min_wait_consecutive=min_wait_consecutive,
        )

        return await self.act_await_response(action)

    async def query_inline(
        self,
        bot: Union[int, str],
        query: str = "",
        offset: str = "",
        latitude: float = None,
        longitude: float = None,
    ) -> InlineResultContainer:
        geo_point = None
        if latitude and longitude:
            geo_point = InputGeoPoint(lat=latitude, long=longitude)

        request = await self.send(
            GetInlineBotResults(
                bot=await self.resolve_peer(bot),
                peer=types.InputPeerSelf(),
                query=query,
                offset=offset,
                geo_point=geo_point,
            )
        )
        return InlineResultContainer(
            self, bot, query, request, offset, geo_point=geo_point
        )

    async def press_inline_button(
        self,
        chat_id: Union[int, str],
        on_message: Union[int, Message],
        callback_data,
        retries=0,
    ) -> Optional[BotCallbackAnswer]:
        if isinstance(on_message, Message):
            mid = on_message.message_id
        elif isinstance(on_message, int):
            mid = on_message
        else:
            raise ValueError("Invalid argument `on_message`")

        request = GetBotCallbackAnswer(
            peer=await self.resolve_peer(chat_id),
            msg_id=mid,
            data=bytes(callback_data, "utf-8"),
        )

        if retries > 0:
            return await self.session.send(request, retries=retries)
        else:
            # noinspection PyProtectedMember
            await self.session._send(request, wait_response=False)
            return None

    async def send_command(
        self, bot: Union[int, str], command: str, params: List[str] = None
    ) -> Message:
        """
        Send a slash-command with corresponding parameters.
        """
        text = "/" + command.lstrip("/")
        if params:
            text += " "
            text += " ".join(params)

        return await self.send_message(bot, text)

    async def send_audio_await(
        self,
        chat_id: Union[int, str],
        audio: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        caption: str = ...,
        parse_mode: str = ...,
        duration: int = ...,
        performer: str = ...,
        title: str = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
    ) -> Response:
        ...

    async def send_chat_action_await(
        self,
        chat_id: Union[int, str],
        action: ChatAction or str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        progress: Callable = ...,
    ) -> Response:
        ...

    async def send_contact_await(
        self,
        chat_id: Union[int, str],
        phone_number: str,
        first_name: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        last_name: str = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
    ) -> Response:
        ...

    async def send_document_await(
        self,
        chat_id: Union[int, str],
        document: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        caption: str = ...,
        parse_mode: str = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
    ) -> Response:
        ...

    async def send_location_await(
        self,
        chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
    ) -> Response:
        ...

    async def send_media_group_await(
        self,
        chat_id: Union[int, str],
        media: list,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
    ) -> Response:
        ...

    async def send_message_await(
        self,
        chat_id: Union[int, str],
        text,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        **kwargs
    ) -> Response:
        ...

    async def send_command_await(
        self,
        chat_id: Union[int, str],
        command: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
    ) -> Response:
        ...

    async def send_photo_await(
        self,
        chat_id: Union[int, str],
        photo: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        caption: str = ...,
        parse_mode: str = ...,
        ttl_seconds: int = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
    ) -> Response:
        ...

    async def send_sticker_await(
        self,
        chat_id: Union[int, str],
        sticker: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
    ) -> Response:
        ...

    async def send_venue_await(
        self,
        chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        foursquare_id: str = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
    ) -> Response:
        ...

    async def send_video_await(
        self,
        chat_id: Union[int, str],
        video: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        caption: str = ...,
        parse_mode: str = ...,
        duration: int = ...,
        width: int = ...,
        height: int = ...,
        thumb: str = ...,
        supports_streaming: bool = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
    ) -> Response:
        ...

    async def send_video_note_await(
        self,
        chat_id: Union[int, str],
        video_note: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        duration: int = ...,
        length: int = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
    ) -> Response:
        ...

    async def send_voice_await(
        self,
        chat_id: Union[int, str],
        voice: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        caption: str = ...,
        parse_mode: str = ...,
        duration: int = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
    ) -> Response:
        ...

    async def send_inline_bot_result_await(
        self,
        chat_id: Union[int, str],
        query_id: int,
        result_id: str,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
    ) -> Response:
        ...

    async def forward_messages_await(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_ids,
        filters: Filter = ...,
        num_expected: int = ...,
        max_wait: float = ...,
        min_wait_consecutive: float = ...,
        raise_: bool = ...,
        disable_notification: bool = None,
    ) -> Response:
        ...


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
            min_wait_consecutive=min_wait_consecutive,
        )
        return await self.act_await_response(action, raise_=raise_)

    method_name += "_await"
    f.__name__ = method_name

    setattr(class_, method_name, f)


for name, method in inspect.getmembers(InteractionClient, predicate=inspect.isfunction):
    if (name.startswith("send_") or name.startswith("forward_")) and not name.endswith(
        "_await"
    ):
        __make_awaitable_method(InteractionClient, name, method)

# endregion
