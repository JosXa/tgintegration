import inspect
import time
from typing import List

from pyrogram import Filters
from pyrogram.api.functions.messages import DeleteHistory
from pyrogram.api.functions.users import GetFullUser
from pyrogram.api.types import BotCommand

from .interactionclient import InteractionClient


class BotIntegrationClient(InteractionClient):
    def __init__(
            self,
            bot_under_test,
            session_name=None,
            api_id=None,
            api_hash=None,
            phone_number=None,
            max_wait_response=15,
            min_wait_consecutive=2,
            global_action_delay=0.2,
            raise_no_response=True,  # TODO: actually implement this
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
        self.raise_no_response = raise_no_response
        self.global_action_delay = global_action_delay

        self.peer = None
        self.peer_id = None
        self.command_list = None

        self._last_response = None

    def get_default_filters(self, user_filters=None):
        if user_filters is None:
            return Filters.chat(self.peer_id) & Filters.incoming
        else:
            return user_filters & Filters.chat(self.peer_id) & Filters.incoming

    def act_await_response(self, action, raise_=None):
        if self.global_action_delay and self._last_response:
            # Sleep for as long as the global delay prescribes
            sleep = self.global_action_delay - (time.time() - self._last_response.started)
            if sleep > 0:
                time.sleep(sleep)

        response = super().act_await_response(
            action,
            raise_=raise_ if raise_ is not None else self.raise_no_response
        )
        self._last_response = response
        return response

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
        self.command_list = self._get_command_list()

        return res

    def ping(self, override_messages=None):
        return super().ping_bot(
            bot=self.peer_id,
            override_messages=override_messages,
            max_wait_response=self.max_wait_response,
            min_wait_consecutive=self.min_wait_consecutive
        )

    def get_inline_results(
            self,
            query,
            offset='',
            location_or_geo=None
    ):
        return self.get_inline_bot_results(
            self.peer_id,
            query=query,
            offset=offset,
            location_or_geo=location_or_geo
        )

    def _get_command_list(self) -> List[BotCommand]:
        return self.send(
            GetFullUser(
                id=self.peer
            )
        ).bot_info.commands

    def clear_chat(self):
        self.send(DeleteHistory(self.peer, max_id=0, just_clear=False))


# region Dynamic code generation

def __modify_await_arg_defaults(class_, method_name, await_method):
    # TODO: functools.wraps
    def f(self, *args, filters=None, num_expected=None, raise_=None, **kwargs):
        # Make sure arguments aren't passed twice
        default_args = dict(
            max_wait=self.max_wait_response,
            min_wait_consecutive=self.min_wait_consecutive,
            raise_=raise_ if raise_ is not None else self.raise_no_response
        )
        default_args.update(**kwargs)

        return await_method(
            self,
            self.peer_id,
            *args,
            filters=self.get_default_filters(filters),
            num_expected=num_expected,
            **default_args
        )

    f.__name__ = method_name
    setattr(class_, method_name, f)


# def __modify_send_arg_defaults(class_, method_name, send_method):
#     def f(self, *args, filters=None, num_expected=None, **kwargs):
#         # Make sure arguments aren't passed twice
#
#         return send_method(
#             self,
#             self.peer_id,
#             *args,
#             filters=self.get_default_filters(filters),
#             num_expected=num_expected,
#             **kwargs
#         )
#
#     f.__name__ = method_name
#     setattr(class_, method_name, f)


for name, method in inspect.getmembers(BotIntegrationClient, inspect.isfunction):
    if not name.startswith('send_'):
        continue
    if name.endswith('_await'):
        __modify_await_arg_defaults(BotIntegrationClient, name, method)
    # else:
    #     __modify_send_arg_defaults(BotIntegrationClient, name, method)

# endregion
