"""Constants for the ``isshub_sync.fetch`` module.

Attributes
----------
HTTP_METHODS: set
    List of all available HTTP methods, uppercase

"""

from enum import auto, IntEnum

from aiohttp import hdrs


HTTP_METHODS: set = hdrs.METH_ALL - {hdrs.METH_CONNECT, hdrs.METH_TRACE}


class DataModes(IntEnum):
    """Different format that can be used to pass data in a http request."""

    JSON = auto()
    FORM = auto()
