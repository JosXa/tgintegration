from logging import Logger
from typing import *

from pyrogram import ChatAction, Client
from pyrogram.api.types import InputGeoPoint, Message
from pyrogram.api.types.messages import BotCallbackAnswer
from pyrogram.client.filters.filter import Filter
from tgintegration import InlineResultContainer
from .awaitableaction import AwaitableAction
from .response import Response


class InteractionClient(Client):
    """
    Ameliorated Pyrogram ``Client`` with convenience methods for sending a message and waiting for
    one or multiple responses from the peer.

    Use this client if there is no single, specific peer you need to interact with, but rather a
    number of bots or users where you want to utilize the waiting-for-arrival capabilities of the
    ``InteractionClient``.
    TODO: Waiting for arrival
    """

    # logger: Logger = ...

    def __init__(self, session_name: str, api_id: int or str = None, api_hash: str = None,
                 proxy: dict = None, test_mode: bool = False, phone_number: str = None,
                 phone_code: str or callable = None, password: str = None, force_sms: bool = False,
                 first_name: str = None, last_name: str = None, workers: int = 4,
                 workdir: str = ".") -> Any:
        """
        Initializes this client instance.

        Args:
            session_name:
                Name to uniquely identify a session of either a User or a Bot.
                For Users: pass a string of your choice, e.g.: "my_main_account".
                For Bots: pass your Bot API token, e.g.: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
                Note: as long as a valid User session file exists, Pyrogram won't ask you again to
                input your phone number.

            api_id:
                The *api_id* part of your Telegram API Key, as integer. E.g.: 12345
                This is an alternative way to pass it if you don't want to use the *config.ini* file.

            api_hash:
                The *api_hash* part of your Telegram API Key, as string. E.g.: "0123456789abcdef0123456789abcdef"
                This is an alternative way to pass it if you don't want to use the *config.ini* file.

            proxy:
                Your SOCKS5 Proxy settings as dict,
                e.g.: *dict(hostname="11.22.33.44", port=1080, username="user", password="pass")*.
                *username* and *password* can be omitted if your proxy doesn't require authorization.
                This is an alternative way to setup a proxy if you don't want to use the *config.ini* file.

            test_mode:
                Enable or disable log-in to testing servers. Defaults to False.
                Only applicable for new sessions and will be ignored in case previously
                created sessions are loaded.

            phone_number:
                Pass your phone number (with your Country Code prefix included) to avoid
                entering it manually. Only applicable for new sessions.

            phone_code:
                Pass the phone code as string (for test numbers only), or pass a callback function
                which must return the correct phone code as string (e.g., "12345").
                Only applicable for new sessions.

            password:
                Pass your Two-Step Verification password (if you have one) to avoid entering it
                manually. Only applicable for new sessions.

            force_sms:
                Pass True to force Telegram sending the authorization code via SMS.
                Only applicable for new sessions.

            first_name:
                Pass a First Name to avoid entering it manually. It will be used to automatically
                create a new Telegram account in case the phone number you passed is not registered yet.
                Only applicable for new sessions.

            last_name:
                Same purpose as *first_name*; pass a Last Name to avoid entering it manually. It can
                be an empty string: "". Only applicable for new sessions.

            workers:
                Thread pool size for handling incoming updates. Defaults to 4.

            workdir:
                Define a custom working directory. The working directory is the location in your filesystem
                where Pyrogram will store your session files. Defaults to "." (current directory).
        """
        super().__init__(session_name, api_id, api_hash, proxy, test_mode, phone_number,
                         phone_code, password, force_sms, first_name, last_name, workers, workdir)
        ...

    def act_await_response(self, action: AwaitableAction, raise_=True) -> Response:
        """
        Executes the request defined by an ``AwaitableAction``, gathers up the responses from
        the peer, and returns a ``Response`` object as soon as the peer is done replying.

        Args:
            action: The action to be executed.
            raise_: Whether to raise a ``NoRespnseReceived`` error or just return ``None`` when
            the peer fails to respond to the action. Defaults to raising the exception.

        Returns:
            A ``Response`` containing all the messages that matched the action's ``filters``.

        """
        ...

    def ping_bot(
            self,
            bot: int or str,
            override_messages: List[str] = None,
            max_wait_response: float = None,
            min_wait_consecutive: float = None,
    ) -> Union[Response, bool]:
        """
        Sends startup commands (/start) to a bot to determine whether it is online.
        If the bot replies, a ``Response`` object with the collected messages is returned,
        otherwise ``False``.

        Args:
            bot: The bot to ping.
            override_messages: A list of messages to send to the bot. Defaults to ``["/start"]``.
            max_wait_response: Maximum time in seconds to wait for a reply.
            min_wait_consecutive: Minimum time in seconds to wait for more than one reply.

        Returns:
            A ``Response`` object if the bot replies, ``False`` otherwise.
        """
        ...

    def send_command(self, bot: Union[int, str], command: str,
                     params: List[str] = None) -> Message:
        """
        Sends a slash-command to a bot
        Args:
            bot:
            command:
            params:

        Returns:

        """
        ...

    def send_audio_await(
            self,
            chat_id: int or str,
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

    def send_chat_action_await(
            self,
            chat_id: int or str,
            action: ChatAction or str,
            filters: Filter = ...,
            num_expected: int = ...,
            max_wait: float = ...,
            min_wait_consecutive: float = ...,
            raise_: bool = ...,
            progress: Callable = ...
    ) -> Response:
        ...

    def send_contact_await(
            self,
            chat_id: int or str,
            phone_number: str,
            first_name: str,
            filters: Filter = ...,
            num_expected: int = ...,
            max_wait: float = ...,
            min_wait_consecutive: float = ...,
            raise_: bool = ...,
            last_name: str = ...,
            disable_notification: bool = ...,
            reply_to_message_id: int = ...
    ) -> Response:
        ...

    def send_document_await(
            self,
            chat_id: int or str,
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
            progress: Callable = ...
    ) -> Response: ...

    def send_location_await(
            self,
            chat_id: int or str,
            latitude: float,
            longitude: float,
            filters: Filter = ...,
            num_expected: int = ...,
            max_wait: float = ...,
            min_wait_consecutive: float = ...,
            raise_: bool = ...,
            disable_notification: bool = ...,
            reply_to_message_id: int = ...
    ) -> Response: ...

    def send_media_group_await(
            self,
            chat_id: int or str,
            media: list,
            filters: Filter = ...,
            num_expected: int = ...,
            max_wait: float = ...,
            min_wait_consecutive: float = ...,
            raise_: bool = ...,
            disable_notification: bool = ...,
            reply_to_message_id: int = ...
    ) -> Response: ...

    def send_message_await(
            self,
            chat_id: int or str,
            text,
            filters: Filter = ...,
            num_expected: int = ...,
            max_wait: float = ...,
            min_wait_consecutive: float = ...,
            raise_: bool = ...,
            **kwargs
    ) -> Response: ...

    def send_command_await(
            self,
            chat_id: int or str,
            command: str,
            filters: Filter = ...,
            num_expected: int = ...,
            max_wait: float = ...,
            min_wait_consecutive: float = ...,
            raise_: bool = ...,
    ) -> Response: ...

    def send_photo_await(
            self,
            chat_id: int or str,
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
            progress: Callable = ...
    ) -> Response: ...

    def send_sticker_await(
            self,
            chat_id: int or str,
            sticker: str,
            filters: Filter = ...,
            num_expected: int = ...,
            max_wait: float = ...,
            min_wait_consecutive: float = ...,
            raise_: bool = ...,
            disable_notification: bool = ...,
            reply_to_message_id: int = ...,
            progress: Callable = ...
    ) -> Response: ...

    def send_venue_await(
            self,
            chat_id: int or str,
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
            reply_to_message_id: int = ...
    ) -> Response: ...

    def send_video_await(
            self,
            chat_id: int or str,
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
            progress: Callable = ...
    ) -> Response: ...

    def send_video_note_await(
            self,
            chat_id: int or str,
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
            progress: Callable = ...
    ) -> Response: ...

    def send_voice_await(
            self,
            chat_id: int or str,
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
            progress: Callable = ...
    ) -> Response: ...

    def get_inline_bot_results(
            self,
            bot: int or str,
            query: str,
            offset: str = "",
            location_or_geo: Union[tuple, InputGeoPoint] = ...
    ) -> InlineResultContainer: ...

    def send_inline_bot_result_await(
            self,
            chat_id: int or str,
            query_id: int,
            result_id: str,
            filters: Filter = ...,
            num_expected: int = ...,
            max_wait: float = ...,
            min_wait_consecutive: float = ...,
            raise_: bool = ...,
            disable_notification: bool = None,
            reply_to_message_id: int = None
    ) -> Response: ...

    def press_inline_button(
            self,
            chat_id: int or str,
            on_message: Union[int, Message],
            callback_data,
            retries=0) -> BotCallbackAnswer: ...
