"""
KeruyunClient — HTTP client for the Keruyun open platform API.

Auth flow:
  1. Fetch token via GET /open/v1/token/get (signed with secretKey)
  2. Cache token keyed by (brand_id, shop_id)
  3. POST to API endpoints (signed with token)
  4. On auth error codes (100-108): invalidate cache and retry once

Signing: see keruyun.signing module.
"""

import json
import time
from typing import Any

import requests

from keruyun.exceptions import KeruyunAPIError, KeruyunAuthError
from keruyun.signing import compute_sign

PROD_URL = "https://openapi.keruyun.com"

# Auth-related error codes that indicate a bad/expired token
_AUTH_ERROR_CODES = {100, 101, 102, 103, 104, 105, 106, 107, 108}


class KeruyunClient:
    """
    Client for the Keruyun open platform API.

    Args:
        app_key: Your application key (appKey).
        app_secret: Your application secret (secretKey), used only for token fetch.
        base_url: API base URL. Defaults to production URL.
    """

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        base_url: str = PROD_URL,
    ):
        self._app_key = app_key
        self._app_secret = app_secret
        self._base_url = base_url.rstrip("/")

        # Token cache: (brand_id, shop_id) → token string
        self._tokens: dict[tuple, str] = {}

        self._session = requests.Session()

        # Namespace objects for endpoint groups
        from keruyun.report import ReportAPI
        from keruyun.order import OrderAPI
        from keruyun.shop import ShopAPI
        from keruyun.supply import SupplyAPI

        self.report = ReportAPI(self)
        self.order = OrderAPI(self)
        self.shop = ShopAPI(self)
        self.supply = SupplyAPI(self)

    def _get_token(self, brand_id: int | None, shop_id: int | None) -> str:
        """
        Fetch and cache access token.

        Token-fetch is a GET request signed with secretKey.
        Result is cached by (brand_id, shop_id) key.

        Args:
            brand_id: Brand ID for brand-level token, or None.
            shop_id: Shop ID for shop-level token, or None.

        Returns:
            Access token string.

        Raises:
            KeruyunAuthError: If the server returns a non-zero error code.
        """
        cache_key = (brand_id, shop_id)
        if cache_key in self._tokens:
            return self._tokens[cache_key]

        params = self._build_base_params(brand_id=brand_id, shop_id=shop_id)
        sign = compute_sign(params, body_json=None, token_or_secret=self._app_secret)
        # secretKey must NOT be sent as a query param — only used in signing
        params["sign"] = sign

        url = self._base_url + "/open/v1/token/get"
        resp = self._session.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code", 0) != 0:
            raise KeruyunAuthError(
                code=data["code"],
                message=data.get("msg", ""),
                path="/open/v1/token/get",
            )

        # Token endpoint returns {"code": 0, "result": {"token": "..."}}
        result = data.get("result") or data.get("data", {})
        token = result["token"]
        self._tokens[cache_key] = token
        return token

    def _build_base_params(
        self,
        brand_id: int | None,
        shop_id: int | None,
    ) -> dict:
        """Build the common query parameters (without sign or token)."""
        params: dict[str, Any] = {
            "appKey": self._app_key,
            "version": "2.0",
            "timestamp": int(time.time()),
        }
        if shop_id is not None:
            params["shopIdenty"] = shop_id
        if brand_id is not None:
            params["brandId"] = brand_id
        return params

    def _build_query_params(
        self,
        brand_id: int | None,
        shop_id: int | None,
    ) -> dict:
        """
        Build full query parameters for an authenticated API call.

        Fetches token (from cache or server) and includes it in params.

        Args:
            brand_id: Brand ID or None.
            shop_id: Shop ID or None.

        Returns:
            Dict with appKey, brandId/shopIdenty, timestamp, version, token.
        """
        token = self._get_token(brand_id=brand_id, shop_id=shop_id)
        params = self._build_base_params(brand_id=brand_id, shop_id=shop_id)
        params["token"] = token
        return params

    def _request(
        self,
        path: str,
        body: dict,
        brand_id: int | None = None,
        shop_id: int | None = None,
    ) -> Any:
        """
        Make an authenticated POST request to the API.

        Delegates to _do_request with retry enabled.

        Args:
            path: API path (e.g. "/open/v1/report/queryFlow").
            body: Request body dict (will be JSON-serialized).
            brand_id: Brand ID or None.
            shop_id: Shop ID or None.

        Returns:
            Parsed response data (the "data" field of the JSON response).

        Raises:
            KeruyunAPIError: On non-zero API error codes.
            KeruyunAuthError: On auth error codes (after retry).
        """
        return self._do_request(path, body, brand_id, shop_id, allow_retry=True)

    def _do_request(
        self,
        path: str,
        body: dict,
        brand_id: int | None,
        shop_id: int | None,
        allow_retry: bool,
    ) -> Any:
        """
        Execute a signed POST request with optional auth retry.

        On auth error codes: invalidates token cache and retries once if allow_retry=True.

        Args:
            path: API path.
            body: Request body dict.
            brand_id: Brand ID or None.
            shop_id: Shop ID or None.
            allow_retry: Whether to retry on auth errors.

        Returns:
            Parsed response data.
        """
        body_json = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
        params = self._build_query_params(brand_id=brand_id, shop_id=shop_id)
        sign = compute_sign(params, body_json=body_json, token_or_secret=params["token"])
        params["sign"] = sign

        url = self._base_url + path
        resp = self._session.post(
            url,
            params=params,
            data=body_json.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

        code = data.get("code", 0)
        # code 0 = standard success; code 2001 = success for orderItem/list endpoint
        if code not in (0, 2001):
            if code in _AUTH_ERROR_CODES:
                # Invalidate cached token so next call fetches fresh
                cache_key = (brand_id, shop_id)
                self._tokens.pop(cache_key, None)

                if allow_retry:
                    return self._do_request(path, body, brand_id, shop_id, allow_retry=False)

                raise KeruyunAuthError(
                    code=code,
                    message=data.get("msg", ""),
                    path=path,
                )

            raise KeruyunAPIError(
                code=code,
                message=data.get("msg", ""),
                path=path,
            )

        # Return the "result" field if present, otherwise the whole response
        return data.get("result", data)
