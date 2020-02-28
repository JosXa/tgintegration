import inspect
from typing import Callable, Union, Optional
from typing import List

from pyrogram import Filters
from pyrogram.api.functions.messages import DeleteHistory
from pyrogram.api.functions.users import GetFullUser
from pyrogram.api.types import BotCommand
from pyrogram.api.types import PeerUser
from pyrogram.client.filters.filter import Filter
from pyrogram.client.methods.messages.send_chat_action import ChatAction

from tgintegration.containers.response import Response
from .containers.inlineresults import InlineResultContainer
from .interactionclient import InteractionClient


class BotController(object):
    def __init__(
        self,
        bot_under_test: Union[int, str],
        client: InteractionClient,
        max_wait_response: float = 20.0,
        min_wait_consecutive: Optional[float] = 2.0,
        raise_no_response: bool = True
    ):
        self.bot_under_test = bot_under_test
        self.client = client
        self.max_wait_response = max_wait_response
        self.min_wait_consecutive = min_wait_consecutive
        self.raise_no_response = raise_no_response

        self.peer: Optional[PeerUser] = None
        self.peer_id: Optional[int] = None
        self.command_list: List[BotCommand] = []

    def get_default_filters(self, user_filters: Filter = None) -> Filter:
        if user_filters is None:
            return Filters.chat(self.peer_id) & Filters.incoming
        else:
            return user_filters & Filters.chat(self.peer_id) & Filters.incoming

    def start(self):
        """Use this method to start the Client after creating it.
        Requires no parameters.

        Raises:
            :class:`Error <pyrogram.Error>`
        """
        self.client.start()
        self.peer = self.client.resolve_peer(self.bot_under_test)
        self.peer_id = self.peer.user_id
        self.command_list = self._get_command_list()

    def ping(self, override_messages: List[str] = None) -> Response:
        return self.client.ping_bot(
            bot=self.peer_id, override_messages=override_messages
        )

    def get_inline_results(
        self, query: str, offset: str = "", latitude: int = None, longitude: int = None
    ) -> InlineResultContainer:
        return self.client.get_inline_bot_results(
            self.peer_id,
            query=query,
            offset=offset,
            latitude=latitude,
            longitude=longitude,
        )

    def _get_command_list(self) -> List[BotCommand]:
        return self.client.send(GetFullUser(id=self.peer)).bot_info.commands

    def clear_chat(self) -> None:
        self.client.send(DeleteHistory(peer=self.peer, max_id=0, just_clear=False))

    def send_audio_await(
        self,
        audio: str,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        caption: str = ...,
        parse_mode: str = ...,
        duration: int = ...,
        performer: str = ...,
        title: str = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
        **kwargs
    ) -> Response:
        ...

    def send_chat_action_await(
        self,
        action: ChatAction or str,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        progress: Callable = ...,
        **kwargs
    ) -> Response:
        ...

    def send_contact_await(
        self,
        chat_id: Union[int, str],
        phone_number: str,
        first_name: str,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        last_name: str = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        **kwargs
    ) -> Response:
        ...

    def send_document_await(
        self,
        document: str,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        caption: str = ...,
        parse_mode: str = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
        **kwargs
    ) -> Response:
        ...

    def send_location_await(
        self,
        latitude: float,
        longitude: float,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        **kwargs
    ) -> Response:
        ...

    def send_media_group_await(
        self,
        media: list,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        **kwargs
    ) -> Response:
        ...

    def send_message_await(
        self,
        text,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        **kwargs
    ) -> Response:
        ...

    def send_command_await(
        self,
        command: str,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        **kwargs
    ) -> Response:
        ...

    def send_photo_await(
        self,
        photo: str,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        caption: str = ...,
        parse_mode: str = ...,
        ttl_seconds: int = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
        **kwargs
    ) -> Response:
        ...

    def send_sticker_await(
        self,
        sticker: str,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
        **kwargs
    ) -> Response:
        ...

    def send_venue_await(
        self,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        foursquare_id: str = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        **kwargs
    ) -> Response:
        ...

    def send_video_await(
        self,
        video: str,
        filters: Filter = ...,
        num_expected: int = ...,
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
        **kwargs
    ) -> Response:
        ...

    def send_video_note_await(
        self,
        video_note: str,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        duration: int = ...,
        length: int = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
        **kwargs
    ) -> Response:
        ...

    def send_voice_await(
        self,
        voice: str,
        filters: Filter = ...,
        num_expected: int = ...,
        raise_: bool = ...,
        caption: str = ...,
        parse_mode: str = ...,
        duration: int = ...,
        disable_notification: bool = ...,
        reply_to_message_id: int = ...,
        progress: Callable = ...,
        **kwargs
    ) -> Response:
        ...


# region Dynamic code generation


def __modify_await_arg_defaults(class_, method_name, await_method):
    # TODO: functools.wraps
    def f(self, *args, filters=None, num_expected=None, raise_=None, **kwargs):
        default_args = dict(
            max_wait=self.max_wait_response,
            min_wait_consecutive=self.min_wait_consecutive,
            raise_=raise_ if raise_ is not None else self.raise_no_response,
        )
        default_args.update(**kwargs)

        client_method = getattr(self.client, method_name)

        return client_method(
            self.peer_id,
            *args,
            filters=self.get_default_filters(filters),
            num_expected=num_expected,
            **default_args
        )

    f.__name__ = method_name
    setattr(class_, method_name, f)


for name, method in inspect.getmembers(BotController, inspect.isfunction):
    if not name.startswith("send_"):
        continue
    if name.endswith("_await"):
        __modify_await_arg_defaults(BotController, name, method)

# endregion
