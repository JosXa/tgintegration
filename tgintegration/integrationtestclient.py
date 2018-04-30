import inspect
import time

from pyrogram import Filters
from pyrogram.api.errors import FloodWait
from pyrogram.api.functions.messages import DeleteHistory
from tgintegration.interactionclient import AwaitableAction, InteractionClient


class IntegrationTestClient(InteractionClient):
    def __init__(
            self,
            session_name,
            api_id,
            api_hash,
            phone_number,
            bot_under_test,
            max_wait_response=15,
            min_wait_consecutive=2,
            global_delay=0.2,
            **kwargs):
        super().__init__(
            session_name=session_name,
            api_id=api_id,
            api_hash=api_hash,
            phone_number=phone_number,
            **kwargs
        )
        self.bot_under_test = bot_under_test
        self.max_wait_response = max_wait_response
        self.min_wait_consecutive = min_wait_consecutive
        self.global_delay = global_delay

        self.peer = None
        self.peer_id = None

        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if 'send_' in name and '_await' not in name:
                self._make_awaitable_method(name, method)

    def _make_awaitable_method(self, name, method):
        """
        Injects `*_await` versions of all `send_*` methods.
        """

        def f(*args, filters=None, num_expected=None, **kwargs):
            action = AwaitableAction(
                func=method,
                args=(self.peer_id, *args),
                kwargs=kwargs,
                num_expected=num_expected,
                filters=self._make_default_filters(filters),
                max_wait=self.max_wait_response,
                min_wait_consecutive=self.min_wait_consecutive
            )
            return self.act_await_response(action)

        method_name = name + '_await'
        setattr(self, method_name, f)

    def _make_default_filters(self, user_filters):
        if user_filters is None:
            return Filters.chat(self.peer_id) & Filters.incoming
        else:
            return user_filters & Filters.chat(self.peer_id) & Filters.incoming

    def send(self, data):
        """Use this method to send Raw Function queries.

        Adapted to include the global delays.

        This method makes possible to manually call every single Telegram API method in a low-level manner.
        Available functions are listed in the :obj:`functions <pyrogram.api.functions>` package and may accept compound
        data types from :obj:`types <pyrogram.api.types>` as well as bare types such as ``int``, ``str``, etc...

        Args:
            data (``Object``):
                The API Scheme function filled with proper arguments.

        Raises:
            :class:`Error <pyrogram.Error>`
        """
        if self.global_delay:
            time.sleep(self.global_delay)
        return super().send(data)

    def start(self, debug=False):
        """Use this method to start the Client after creating it.
        Requires no parameters.

        Args:
            debug (``bool``, optional):
                Enable or disable debug mode. When enabled, extra logging
                lines will be printed out on your console.

        Raises:
            :class:`Error <pyrogram.Error>`
        """
        res = super().start(debug=debug)

        self.peer = self.resolve_peer(self.bot_under_test)
        self.peer_id = self.peer.user_id

        return res

    def send_command_await(self, command, params=None, filters=None, num_expected=None):
        """
        Send a slash-command with corresponding parameters.

        Args:
            command:
            params:
            filters:
            num_expected:

        Returns:

        """
        text = "/" + command.lstrip('/')
        if params:
            text += ' '
            text += ' '.join(params)
        return self.send_message_await(text, filters=filters, num_expected=num_expected)

    def ping(self, override_messages=None):
        """
        Send messages to a bot to determine whether it is online.

        Specify a list of ``override_messages`` that should be sent to the bot, defaults to /start.

        Args:
            override_messages: List of messages to be sent

        Returns:
            Response
        """

        # TODO: should this method also handle inline queries?

        return super().ping_bot(
            peer=self.peer_id,
            override_messages=override_messages,
            max_wait_response=self.max_wait_response,
            min_wait_consecutive=self.min_wait_consecutive
        )

    def clear_chat(self):
        self.send(DeleteHistory(self.peer, max_id=999999999, just_clear=True))
