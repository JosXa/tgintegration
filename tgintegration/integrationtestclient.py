import inspect
import time

from pyrogram import Filters
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
        """
        Overrides the client's `send` method to account for global delays
        """
        if self.global_delay:
            time.sleep(self.global_delay)
        return super().send(data)

    def start(self, debug=False):
        res = super().start(debug=debug)

        self.peer = self.resolve_peer(self.bot_under_test)
        self.peer_id = self.peer.user_id

        return res

    def send_command_await(self, command, params=None, filters=None, num_expected=None):
        text = "/" + command.lstrip('/')
        if params:
            text += ' '
            text += ' '.join(params)
        return self.send_message_await(text, filters=filters, num_expected=num_expected)

    def clear_chat(self):
        self.send(DeleteHistory(self.peer, max_id=999999999, just_clear=True))
