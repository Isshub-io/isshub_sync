"""Python types for the ``isshub_sync.fetch`` module."""

import _collections_abc as abc
from typing import Optional, Type, Union

from ..utils import NotProvided
from .constants import HTTP_METHODS


# pylint: disable=invalid-name
CallableArg = Union[str, int]
OptionalDict = Optional[Union[Type[NotProvided], dict]]
OptionalStr = Optional[Union[Type[NotProvided], str]]
Url = str
# pylint: enable=invalid-name


class ConnectionClient(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods
    """Abstract parent class for connection clients.

    So it's usable as a type for things like:
    - ``aiohttp.ClientSession``
    - ``pytest_aiohttp.TestClient``

    Such a class is considered as valid if it has one method for each
    available http method (the method must be lowercase)

    Examples
    --------
    >>> from aiohttp import ClientSession
    >>> issubclass(ClientSession, ConnectionClient)
    True
    >>> from pytest_aiohttp import TestClient
    >>> issubclass(TestClient, ConnectionClient)
    True
    >>> class WrongClient:
    ...     def get(self): pass
    >>> issubclass(WrongClient, ConnectionClient)
    False

    """

    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, subclass: Type)->bool:
        """Will check if the class `C` is a subclass of ``ConnectionClient``.

        We do this by iterating on all http methods and if at least one
        is not defined as a method in `C`, then we return ``False``

        Parameters
        ----------
        subclass : Type
            The class to check

        Returns
        -------
        bool
            ``True`` if `C` is a subclass of ``ConnectionClient``, ``False`` otherwise

        """

        return abc._check_methods(subclass, *[  # pylint: disable=protected-access
            method.lower() for method in HTTP_METHODS
        ]) is not NotImplemented
