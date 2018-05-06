from typing import Callable, List, Dict

from pyrogram.client.filters.filter import Filter

from pyrogram import Filters


class AwaitableAction:
    """
    Represents an action to be sent by the client while waiting for a response by the peer.
    """

    func : Callable
    args : List
    kwargs : Dict
    filters : Filter
    num_expected : int  # private property
    consecutive_wait : int
    max_wait : int

    def __init__(
            self,
            func: Callable,
            args: List = None,
            kwargs: Dict = None,
            filters: Filter = None,
            num_expected: int = None,
            max_wait: int = 20,
            min_wait_consecutive: int = None,
    ):
        ...
