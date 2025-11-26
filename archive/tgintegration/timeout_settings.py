from dataclasses import dataclass
from typing import Optional


@dataclass
class TimeoutSettings:
    max_wait: float = 10
    """
    The maximum duration in seconds to wait for a response from the peer.
    """

    wait_consecutive: Optional[float] = None
    """
    The minimum duration in seconds to wait for another consecutive message from the peer after
    receiving a message. This can cause the total duration to exceed the `max_wait` time.
    """

    raise_on_timeout: bool = False
    """
    Whether to raise an exception when a timeout occurs or to fail with a log message.
    """
