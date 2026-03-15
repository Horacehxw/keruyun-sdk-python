"""
Tests for KeruyunClient — token management and request handling.

Uses the `responses` library to mock HTTP calls without making real network requests.
"""

import json
import pytest
import responses as responses_lib
from urllib.parse import urlparse, parse_qs

from keruyun import KeruyunClient, KeruyunAPIError, KeruyunAuthError

BASE_URL = "https://openapi.keruyun.com"
TOKEN_PATH = "/open/v1/token/get"
BRAND_ID = 32296
SHOP_ID = 810094
APP_KEY = "testkey"
APP_SECRET = "testsecret"
BRAND_TOKEN = "brand-token-abc"
SHOP_TOKEN = "shop-token-xyz"


def _token_url():
    return BASE_URL + TOKEN_PATH


def _make_token_response(token: str, code: int = 0, msg: str = "success"):
    """Token endpoint returns {"code": 0, "result": {"token": "..."}}"""
    return {"code": code, "msg": msg, "result": {"token": token}}


def _make_api_response(result: dict, code: int = 0, msg: str = "success"):
    """Standard API endpoints return {"code": 0, "result": {...}}"""
    return {"code": code, "msg": msg, "result": result}


@pytest.fixture
def client():
    return KeruyunClient(app_key=APP_KEY, app_secret=APP_SECRET, base_url=BASE_URL)


@responses_lib.activate
def test_brand_token_fetch(client):
    """GET /open/v1/token/get returns brand token and caches it."""
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response(BRAND_TOKEN),
        status=200,
    )

    token = client._get_token(brand_id=BRAND_ID, shop_id=None)
    assert token == BRAND_TOKEN
    assert len(responses_lib.calls) == 1


@responses_lib.activate
def test_shop_token_fetch(client):
    """GET /open/v1/token/get returns shop token and caches it."""
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response(SHOP_TOKEN),
        status=200,
    )

    token = client._get_token(brand_id=None, shop_id=SHOP_ID)
    assert token == SHOP_TOKEN
    assert len(responses_lib.calls) == 1


@responses_lib.activate
def test_token_cached_on_second_call(client):
    """Second call to _get_token with same params uses cache — only 1 HTTP call total."""
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response(BRAND_TOKEN),
        status=200,
    )

    token1 = client._get_token(brand_id=BRAND_ID, shop_id=None)
    token2 = client._get_token(brand_id=BRAND_ID, shop_id=None)
    assert token1 == token2 == BRAND_TOKEN
    assert len(responses_lib.calls) == 1  # Only one actual HTTP request


@responses_lib.activate
def test_token_fetch_failure_raises_auth_error(client):
    """Non-zero code in token response raises KeruyunAuthError."""
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response("", code=101, msg="invalid app key"),
        status=200,
    )

    with pytest.raises(KeruyunAuthError) as exc_info:
        client._get_token(brand_id=BRAND_ID, shop_id=None)

    assert exc_info.value.code == 101
    assert "invalid app key" in str(exc_info.value)


@responses_lib.activate
def test_secret_key_not_in_token_url(client):
    """secretKey must NOT appear in the token request URL query params."""
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response(BRAND_TOKEN),
        status=200,
    )

    client._get_token(brand_id=BRAND_ID, shop_id=None)

    token_call = responses_lib.calls[0]
    parsed = urlparse(token_call.request.url)
    query_params = parse_qs(parsed.query)
    assert "secretKey" not in query_params, "secretKey must NOT be sent as a URL query param"
    assert "sign" in query_params, "sign must be present in URL query params"
    assert "appKey" in query_params


@responses_lib.activate
def test_successful_post_request(client):
    """POST to API with valid response returns parsed result dict."""
    api_path = "/open/v1/report/queryFlow"
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response(BRAND_TOKEN),
        status=200,
    )
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + api_path,
        json=_make_api_response({"total": 9999}),
        status=200,
    )

    result = client._request(api_path, body={"date": "2026-03-15"}, brand_id=BRAND_ID, shop_id=None)
    assert result == {"total": 9999}


@responses_lib.activate
def test_request_body_is_compact_json(client):
    """POST body must be compact JSON (no extra spaces) to match signing."""
    api_path = "/open/v1/report/queryFlow"
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response(BRAND_TOKEN),
        status=200,
    )
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + api_path,
        json=_make_api_response({"ok": True}),
        status=200,
    )

    body = {"date": "2026-03-15", "shopId": 12345}
    client._request(api_path, body=body, brand_id=BRAND_ID, shop_id=None)

    api_call = responses_lib.calls[1]
    sent_body = api_call.request.body
    if isinstance(sent_body, bytes):
        sent_body = sent_body.decode("utf-8")
    # Compact JSON has no spaces after : or ,
    assert sent_body == json.dumps(body, separators=(",", ":"), ensure_ascii=False)


@responses_lib.activate
def test_api_error_raises_exception(client):
    """Non-zero code in API response raises KeruyunAPIError (not AuthError)."""
    api_path = "/open/v1/report/queryFlow"
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response(BRAND_TOKEN),
        status=200,
    )
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + api_path,
        json=_make_api_response({}, code=500, msg="internal server error"),
        status=200,
    )

    with pytest.raises(KeruyunAPIError) as exc_info:
        client._request(api_path, body={}, brand_id=BRAND_ID, shop_id=None)

    assert exc_info.value.code == 500
    assert "internal server error" in str(exc_info.value)


@responses_lib.activate
def test_request_sends_sign_in_query_params(client):
    """Request URL must include 'sign' and 'appKey' as query params."""
    api_path = "/open/v1/report/queryFlow"
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response(BRAND_TOKEN),
        status=200,
    )
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + api_path,
        json=_make_api_response({"ok": True}),
        status=200,
    )

    client._request(api_path, body={}, brand_id=BRAND_ID, shop_id=None)

    api_call = responses_lib.calls[1]
    assert "sign=" in api_call.request.url
    assert "appKey=" in api_call.request.url


@responses_lib.activate
def test_auth_retry_on_expired_token(client):
    """
    Auth error on first API call → invalidate token cache → refetch token → retry → success.
    Total HTTP calls: 1 (initial token) + 1 (failed API) + 1 (retry token) + 1 (retry API) = 4.
    """
    api_path = "/open/v1/report/queryFlow"
    # Initial token fetch
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response("expired-token"),
        status=200,
    )
    # First API call → auth error (token expired)
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + api_path,
        json=_make_api_response({}, code=100, msg="token expired"),
        status=200,
    )
    # Retry token fetch → new token
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response("new-token"),
        status=200,
    )
    # Retry API call → success
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + api_path,
        json=_make_api_response({"total": 100}),
        status=200,
    )

    result = client._request(api_path, body={}, brand_id=BRAND_ID, shop_id=None)
    assert result == {"total": 100}
    assert len(responses_lib.calls) == 4


@responses_lib.activate
def test_brand_params(client):
    """_build_query_params for brand call includes brandId, token, version, timestamp."""
    responses_lib.add(
        responses_lib.GET,
        _token_url(),
        json=_make_token_response(BRAND_TOKEN),
        status=200,
    )

    params = client._build_query_params(brand_id=BRAND_ID, shop_id=None)
    assert params["brandId"] == BRAND_ID
    assert params["token"] == BRAND_TOKEN
    assert params["version"] == "2.0"
    assert "timestamp" in params
    assert isinstance(params["timestamp"], int)
