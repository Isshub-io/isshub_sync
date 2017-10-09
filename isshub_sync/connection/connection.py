"""Objects to handle a http requests, with path creation.

The callable + executable pattern for generating request paths is
inspired from the ``github.py`` library.

It starts with a ``Connection``, then some parts (as attribute or
calls), then an HTTP method.

"""

import json
from typing import Awaitable, Optional, Type, Union
from urllib.parse import urlparse, urlunparse, ParseResult  # noqa: F401

from aiohttp import ClientResponse, ClientSession

from ..utils import NotProvided
from .constants import DataModes, HTTP_METHODS
from .python_types import CallableArg, ConnectionClient, OptionalDict, OptionalStr, Url


class Connection:  # pylint: disable=too-few-public-methods
    """A object capable of calling a HTTP endpoint.

    If an attribute is accessed or a call is made, a ``Callable`` object
    is created to construct a path. See examples.

    It is also totally possible to use this "normally", using ``connection.get(path, ...)``

    Parameters
    ----------
    root: Url
        The base url for all calls in this connection. A string with scheme, domain name
        and optional port
    client: type(ConnectionClient), optional
        The client to use to make the connection. Will default to an instance of
        ``cls.DEFAULT_CLIENT_CLASS``

    Attributes
    ----------
    PATH_SUFFIX: str = '/'
        A string to force to be present at the end of the path of a request.
        Default to "/"
    DEFAULT_CLIENT_CLASS: ConnectionClient = ClientSession
        The default class to use as a client to make the request if not passed to the
        constructor. If not defined, on the first request an instance will be created without
        any parameter. If some are needed, simply override ``request`` by passing your own
        client.
    root: Url
        The base url for all calls in this connection. It's the value given on the constructor
        but validated, and maybe changed, by the ``_validate_root`` method
    client: ConnectionClient
        The client used to make the requests. If not set in the constructor, it will be initialized
        on the first request using ``DEFAULT_CLIENT_CLASS``



    Examples
    --------
    >>> connection = Connection('https://httpbin.org/')
    >>> connection.foo
    Callable (/foo/)
    >>> connection('bar')
    Callable (/bar/)
    >>> connection('bar/baz')
    Callable (/bar/baz/)
    >>> connection.bar('baz', 1).get
    Executable (GET /bar/baz/1/)

    Notes
    -----
    Some keywords cannot be used as attributes of a ``Connection`` to create a path:
    - client
    - root
    - request
    - all HTTP methods (in their lower form)

    If the first part of the path needs to be one of these, you can use them in a callable way:

    >>> connection('client').get
    Executable (GET /client/)
    >>> connection('get').get
    Executable (GET /get/)


    """

    __slots__ = (
        'client',
        'root'
    )

    PATH_SUFFIX: str = '/'
    DEFAULT_CLIENT_CLASS: Type[ConnectionClient] = ClientSession

    def __init__(self, root: Url, client: Optional[ConnectionClient] = None) -> None:
        """Save given client and root."""

        self.client: Optional[ConnectionClient] = client
        self.root: Url = self._validate_root(root)

    @staticmethod
    def _validate_root(root: Url) -> Url:
        """Ensure the given `root` is valid and return it sanitized.

        Parameters
        ----------
        root : Url
            The `root` to validate

        Returns
        -------
        Url
            A validated root

        """

        parsed: ParseResult = urlparse(root)

        assert parsed.scheme in {'http', 'https'}

        path: str = parsed.path or ''
        if path.endswith('/'):
            path = path[:-1]

        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            path,
            '',
            '',
            ''
        ))

    def __getattr__(self, attr: str) -> Union['Callable', 'Executable']:
        """Return a new ``Callable``, or an ``Executable`` if `attr` is a method.

        Parameters
        ----------
        attr : str
            If in ``HTTP_METHODS``, will be used to create a new ``Executable``.
            Else it will create a new ``Callable``, using `attr` for the path

        Returns
        -------
        Union[Callable, Executable]
            The newly created object

        """

        if attr.upper() in HTTP_METHODS:
            return Executable(self, attr.upper())

        return Callable(self, attr)

    def __call__(self, *args: CallableArg) -> 'Callable':
        """Return a new ``Callable`` with the given args.

        Parameters
        ----------
        args : Iterable[CallableArg]
            A "list" of parts to add to the path

        Returns
        -------
        Callable
            A new ``Callable`` object initialized with `*args`

        """

        return Callable(self, *args)

    async def request(  # pylint: disable=too-many-arguments
            self,
            method: str,
            path: str,
            data: OptionalDict = NotProvided,
            data_mode: Optional[DataModes] = DataModes.FORM,
            headers: OptionalDict = NotProvided,
            path_suffix: OptionalStr = NotProvided) -> Awaitable[ClientResponse]:
        """[ASYNC] Generate a request.

        Parameters
        ----------
        method : str
            The method to use. Will be lowercased
        path : str
            The path in the request. Must not contain the host. If will be prefixed with "/"
            if not present.
        data : dict, optional
            Data to pass as the body of the request, if set.
        data_mode: DataModes
            One key of the ``DataMode`` enum, for example ``DataMode.FORM`` or ``DataMode.JSON``
        headers : dict, optional
            HTTP headers for the request.
        path_suffix : str, optional
            A string to be added at the end of the path if not already present.
            Will default to ``self.PATH_SUFFIX`` if not provided


        Returns
        -------
        Awaitable[ClientResponse]
            The async response of the request

        """

        method = method.lower()

        if self.client is None:
            self.client = self.DEFAULT_CLIENT_CLASS()

        if not path.startswith('/'):
            path = '/' + path

        _path_suffix: str = self.PATH_SUFFIX if path_suffix is NotProvided else str(path_suffix)
        if _path_suffix and not path.endswith(_path_suffix):
            path += _path_suffix

        url = self.root + path

        kwargs: dict = {}

        if data is not NotProvided:
            if data_mode is DataModes.JSON:
                kwargs['data'] = json.dumps(data)
            else:
                kwargs['data'] = data

        if headers is not NotProvided:
            kwargs['headers'] = headers

        response = await getattr(self.client, method)(url, **kwargs)

        return response


class Executable:  # pylint: disable=too-few-public-methods
    """A ready to be executed http request.

    Parameters
    ----------
    connection: Connection
        The connection to use to make the request
    method: str
        The HTTP method used. One of ``isshub_sync.connection.constants.HTTP_METHODS``
    path: str, optional
        The path of the request. If not set, the request will be made to ``connection.root``.

    Attributes
    ----------
    All parameters given to the constuctor are saved as attributes on the instance.

    Examples
    --------
    >>> connection = Connection('https://httpbin.org/')
    >>> Executable(connection, 'GET', '/foo/bar')
    Executable (GET /foo/bar/)

    """

    __slots__ = (
        'connection',
        'method',
        'path',
    )

    def __init__(self, connection: Connection, method: str, path: Optional[str] = None) -> None:
        """Save all arguments to be ready to be called."""

        self.connection: Connection = connection
        self.method: str = method
        self.path: Optional[str] = path

    def __str__(self) -> str:
        """Return the class name and the actual method and path.

        Returns
        -------
        str
            The stringified version of the object

        """

        path = self.path or '/'

        return 'Executable (%s %s%s)' % (
            self.method,
            path,
            '' if path.endswith(self.connection.PATH_SUFFIX) else self.connection.PATH_SUFFIX
        )

    __repr__ = __str__

    async def __call__(self, *args, **kwargs) -> ClientResponse:
        """[ASYNC] Launch the request.

        Parameters are all passed to ``self.connection.request``

        If we doesn't have any path:
            - we try to extract if from `kwargs`
            - we try to extract the first entry of `args
            - we set it to "/"

        Returns
        -------
        ClientResponse
            The async response of the request

        """

        path: str = self.path
        if not path:
            if 'path' in kwargs:
                path = kwargs.pop('path')
            elif args:
                path, *args = args

        if not path:
            path = '/'

        return await self.connection.request(self.method, path, *args, **kwargs)


class Callable:  # pylint: disable=too-few-public-methods
    """Object that will create a new one when calling or accessing attribute.

    The only exception is when accessing attributes that are http methods. In this case,
    a new ``Executable`` object will be created.

    The actual path of a ``Callable`` can be accessed via the ``_path`` property (prefixed with
    "_" to be able to use "path" as a part of a real path)

    Attributes
    ----------
    All parameters given to the constuctor are saved as attributes on the instance.

    Examples
    --------
    >>> connection = Connection('https://httpbin.org/')
    >>> a_callable = Callable(connection, 'foo')
    >>> new_callable = a_callable.bar(1)
    >>> new_callable.path
    '/foo/bar/1'
    >>> new_callable
    Callable (/foo/bar/1/)
    >>> new_callable.get
    Executable (GET /foo/bar/1/)
    >>> Callable(connection)('foo', 'bar', 2)
    Callable (/foo/bar/2/)

    Notes
    -----
    Some keywords cannot be used as attributes of a ``Callable`` to create a path:
    - connection
    - parts
    - path
    - all HTTP methods (in their lower form)

    If the first part of the path needs to be one of these, you can use them in a callable way:

    >>> Callable(connection)('parts')
    Callable (/parts/)
    >>> Callable(connection)('get')
    Callable (/get/)

    """

    __slots__ = (
        'connection',
        'parts',
    )

    def __init__(self, connection: Connection, *parts: CallableArg) -> None:
        """Convert the parts and save them, along the connection.

        Parameters
        ----------
        connection : Connection
            The connection that will eventually be passed to the ``Executable``
        parts : CallableArg
            A iterable of int or strings. Ints will be converted to strings, and strings
            will be split on "/"

        """

        self.connection: Connection = connection
        self.parts: list = sum([str(part).split('/') for part in parts], [])

    def __call__(self, *args: CallableArg) -> 'Callable':
        """Return a new ``Callable`` with the given args added to the current ones.

        Parameters
        ----------
        args : Iterable[CallableArg]
            A "list" of parts to add to the path

        Returns
        -------
        Callable
            A new ``Callable`` with the current parts and the new ones

        """

        return Callable(self.connection, *self.parts, *args) if args else self

    def __getattr__(self, attr: str) -> Union['Callable', Executable]:
        """Return a new ``Callable``, or an ``Executable`` if `attr` is a method.

        Parameters
        ----------
        attr : str
            If in ``HTTP_METHODS``, will be used to create a new ``Executable``.
            Else it will create a new ``Callable``, adding `attr` to the path

        Returns
        -------
        Union[Callable, Executable]
            The newly created object

        """

        if attr.upper() in HTTP_METHODS:
            return Executable(self.connection, attr.upper(), self.path)

        return Callable(self.connection, *self.parts, attr)

    @property
    def path(self) -> str:
        """Convert the parts into a path, the whole being prefixed by "/".

        Returns
        -------
        str
            The ``parts`` attribute converted into a string, joined by "/"

        """

        return '/' + '/'.join(self.parts)

    def __str__(self) -> str:
        """Return the class name and the actual path.

        Returns
        -------
        str
            The stringified version of the object

        """

        return '%s (%s%s)' % (self.__class__.__name__, self.path, self.connection.PATH_SUFFIX)

    __repr__ = __str__
