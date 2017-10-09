from aiohttp import web, ClientSession

import pytest

from isshub_sync.connection.connection import (
    Callable,
    Connection,
    Executable,
    HTTP_METHODS,
)
from isshub_sync.connection.constants import DataModes

DUMMY_ROOT: str = 'https://httpbin.org/'


def test_connection_validate_its_root():

    connection = Connection(DUMMY_ROOT)
    assert connection.root == 'https://httpbin.org'

    with pytest.raises(AssertionError):
        Connection('foo')

    connection = Connection('HTTPS://foo.com/bar/')
    assert connection.root == 'https://foo.com/bar'


def test_connection_converts_to_callable():

    connection = Connection(DUMMY_ROOT)
    value = connection.foo('bar')

    assert isinstance(value, Callable)
    assert value.parts == ['foo', 'bar']
    assert value.path == '/foo/bar'
    assert connection is value.connection

    value = connection('foo')
    assert isinstance(value, Callable)
    assert value.parts == ['foo']
    assert value.path == '/foo'
    assert connection is value.connection


def test_callable_accepts_many_parts():

    connection = Connection(DUMMY_ROOT)
    value = Callable(connection, 'foo')

    assert value.parts == ['foo']
    assert value.path == '/foo'

    value = Callable(connection, 'foo', 1)

    assert value.parts == ['foo', '1']
    assert value.path == '/foo/1'

    value = Callable(connection, 'foo/bar', 'baz')

    assert value.parts == ['foo', 'bar', 'baz']
    assert value.path == '/foo/bar/baz'


def test_callable_is_chainable():

    connection = Connection(DUMMY_ROOT)
    value = Callable(connection, 'foo').bar('baz', 1)

    assert isinstance(value, Callable)
    assert value.parts == ['foo', 'bar', 'baz', '1']
    assert value.path == '/foo/bar/baz/1'


@pytest.mark.parametrize('method', HTTP_METHODS)
def test_callable_with_attr_method_converts_to_executable(method: str):

    connection = Connection(DUMMY_ROOT)
    value = getattr(Callable(connection, 'foo/bar/baz'), method)

    assert isinstance(value, Executable)
    assert value.path == '/foo/bar/baz'
    assert connection is value.connection
    assert value.method == method

    value = getattr(Callable(connection, 'foo/bar/baz'), method.lower())
    assert isinstance(value, Executable)
    assert value.method == method

    value = getattr(Callable(connection, 'foo/bar/baz'), method.capitalize())
    assert isinstance(value, Executable)
    assert value.method == method


@pytest.mark.parametrize('method', HTTP_METHODS)
def test_callable_with_call_method_does_not_convert_to_executable(method: str):

    connection = Connection(DUMMY_ROOT)
    value = Callable(connection, 'foo/bar/baz')(method)

    assert isinstance(value, Callable)
    assert value.path == '/foo/bar/baz/%s' % method

    value = Callable(connection, 'foo/bar/baz')(method.lower())
    assert isinstance(value, Callable)
    assert value.path == '/foo/bar/baz/%s' % method.lower()

    value = Callable(connection, 'foo/bar/baz')(method.capitalize())
    assert isinstance(value, Callable)
    assert value.path == '/foo/bar/baz/%s' % method.capitalize()


def test_executable_path_is_optional():

    connection = Connection(DUMMY_ROOT)
    executable = Executable(connection, 'GET')
    assert str(executable) == 'Executable (GET /)'


@pytest.fixture
def client(loop, test_client):

    async def dummy_get(request):
        return web.Response(text='dummy')

    async def dummy_post_form(request):
        value = (await request.post())['foo']
        return web.Response(text='foo was set to %s' % value)

    async def dummy_post_json(request):
        value = (await request.json())['foo']
        return web.Response(text='foo was set to %s' % value)

    app = web.Application()
    app.router.add_get('/', dummy_get)
    app.router.add_get('/dummy_get/', dummy_get)
    app.router.add_post('/dummy_post_form/', dummy_post_form)
    app.router.add_post('/dummy_post_json/', dummy_post_json)
    app.router.add_get('/dummy_no_end_slash', dummy_get)

    return loop.run_until_complete(test_client(app))


def test_connection_accept_root_without_leading_slash():
    connection = Connection(DUMMY_ROOT.strip('/'), client=client)
    assert connection.root == 'https://httpbin.org'


def test_connection_accept_root_with_leading_slash():
    connection = Connection(DUMMY_ROOT, client=client)
    assert connection.root == 'https://httpbin.org'


async def test_connection_should_make_a_call(client):

    connection = Connection(DUMMY_ROOT, client=client)
    connection.root = ''  # test client refuses absolute urls
    response = await connection.dummy_get.get()

    assert response.status == 200
    text = await response.text()
    assert text == 'dummy'


async def test_connection_path_is_optional(client):

    connection = Connection(DUMMY_ROOT, client=client)
    connection.root = ''  # test client refuses absolute urls
    response = await connection.get()

    assert response.status == 200
    text = await response.text()
    assert text == 'dummy'


async def test_connection_should_be_able_to_post_form_data(client):

    connection = Connection(DUMMY_ROOT, client=client)
    connection.root = ''  # test client refuses absolute urls
    response = await connection.dummy_post_form.post(data={'foo': 'bar'})

    assert response.status == 200
    text = await response.text()
    assert text == 'foo was set to bar'


async def test_connection_should_be_able_to_post_json(client):

    connection = Connection(DUMMY_ROOT, client=client)
    connection.root = ''  # test client refuses absolute urls
    response = await connection.dummy_post_json.post(data={'foo': 'bar'}, data_mode=DataModes.JSON)

    assert response.status == 200
    text = await response.text()
    assert text == 'foo was set to bar'


async def test_connection_default_client(client):
    connection = Connection(DUMMY_ROOT)
    await connection.get()
    assert isinstance(connection.client, ClientSession)


async def test_connection_prefix_and_suffix_path(client):
    connection = Connection(DUMMY_ROOT, client=client)
    connection.root = ''  # test client refuses absolute urls
    response = await connection.request('GET', 'dummy_get')

    assert response.url.path == '/dummy_get/'
    assert response.status == 200
    text = await response.text()
    assert text == 'dummy'


async def test_connection_can_define_own_path_suffix(client):

    class NoSlashConnection(Connection):
        PATH_SUFFIX = ''

    connection = NoSlashConnection(DUMMY_ROOT, client=client)
    connection.root = ''  # test client refuses absolute urls
    response = await connection.request('GET', '/dummy_no_end_slash')

    assert response.url.path == '/dummy_no_end_slash'
    assert response.status == 200
    text = await response.text()
    assert text == 'dummy'


async def test_connection_can_receive_headers(client):
    connection = Connection(DUMMY_ROOT, client=client)
    connection.root = ''  # test client refuses absolute urls
    response = await connection.dummy_get.get(headers={'X-Foo': 'Bar'})

    assert response.status == 200
    assert response.request_info.headers['X-Foo'] == 'Bar'


async def test_connection_can_make_a_call_with_everything(client):
    connection = Connection(DUMMY_ROOT, client=client)
    connection.root = ''  # test client refuses absolute urls

    # pass path as arg
    response = await connection.get('/dummy_get/', headers={'X-Foo': 'Bar'})

    assert response.status == 200
    assert response.url.path == '/dummy_get/'
    assert response.request_info.headers['X-Foo'] == 'Bar'
    text = await response.text()
    assert text == 'dummy'

    # pass path as kwarg
    response = await connection.get(path='/dummy_get/')
    assert response.status == 200
    assert response.url.path == '/dummy_get/'
