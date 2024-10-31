import httpx
import pytest
from operations.http_request.base import safe_json_request, configure_client
url = '/test'
host='http://localhost'
test_json = dict(result='success')
error_json = dict(error='error')
error_body = "error"
success_body = "success"

@pytest.fixture(autouse=True)
def client(token):
    configure_client(url=host, cert=None, server_version=9.9, token=token)

@pytest.fixture(params=[200])
def success_codes(request):
    return request.param


@pytest.fixture(params=[400, 500])
def error_codes(request):
    return request.param


@pytest.fixture(params=['put', 'post', 'patch', 'get', 'delete'])
def request_methods(request):
    return request.param


async def test_request_success(respx_mock, request_methods, success_codes):
    getattr(respx_mock, request_methods)(url=url).side_effect = httpx.Response(success_codes, json=test_json)
    status_code, js = await safe_json_request(host=host, method=request_methods, url=url, )
    assert 200 <= status_code < 300
    assert js == test_json


async def test_request_no_json(respx_mock, request_methods, success_codes):
    getattr(respx_mock, request_methods)(url=url).side_effect = httpx.Response(success_codes, text=success_body)
    status_code, js = await safe_json_request(host=host, method=request_methods, url=url, )
    assert 200 <= status_code < 300
    assert js == dict(content=success_body)


async def test_request_failure_codes_json(respx_mock, request_methods, error_codes):
    getattr(respx_mock, request_methods)(url=url).side_effect = httpx.Response(error_codes, json=error_json)
    status_code, js = await safe_json_request(host=host, method=request_methods, url=url)
    assert 400 <= status_code < 600
    assert js == error_json


async def test_request_failure_codes_no_json(respx_mock, request_methods, error_codes):
    getattr(respx_mock, request_methods)(url=url).side_effect = httpx.Response(error_codes, text=error_body)
    status_code, js = await safe_json_request(host=host, method=request_methods, url=url)
    assert 400 <= status_code < 600
    assert js == dict(content=error_body)


async def test_request_retries_server_error_automatically(respx_mock, request_methods):
    getattr(respx_mock, request_methods)(url=url).side_effect = [
        httpx.Response(500, json=error_body),
        httpx.Response(200, json=test_json),
    ]
    status_code, js = await safe_json_request(host=host, method=request_methods, url=url, )
    assert status_code == 200


@pytest.mark.respx()
async def test_request_timeout_return_code_empty_dict(respx_mock, request_methods):
    getattr(respx_mock, request_methods)(url=url).mock(side_effect=httpx.TimeoutException)
    status_code, js = await safe_json_request(host=host, method=request_methods, url=url, )

    assert status_code is None
    assert js == dict()