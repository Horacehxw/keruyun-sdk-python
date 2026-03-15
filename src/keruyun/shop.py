"""
ShopAPI — endpoints for querying store/shop information.

Note: get_store_list uses brand-level auth, but get_store_detail uses
shop-level auth (shopIdenty). brandId and shopIdenty cannot coexist.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from keruyun.client import KeruyunClient

from keruyun.exceptions import KeruyunAPIError, KeruyunAuthError
from keruyun.signing import compute_sign


class ShopAPI:
    def __init__(self, client: KeruyunClient):
        self._client = client

    def _request(
        self,
        path: str,
        body: dict,
        brand_id: int | None = None,
        shop_id: int | None = None,
    ) -> Any:
        """
        Make an authenticated POST request to a shop endpoint.

        Shop API responses use 'result' instead of 'data' as the payload key.
        """
        client = self._client
        body_json = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
        params = client._build_query_params(brand_id=brand_id, shop_id=shop_id)
        sign = compute_sign(params, body_json=body_json, token_or_secret=params["token"])
        params["sign"] = sign

        url = client._base_url + path
        resp = client._session.post(
            url,
            params=params,
            data=body_json.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

        code = data.get("code", 0)
        if code != 0:
            if code in {100, 101, 102, 103, 104, 105, 106, 107, 108}:
                raise KeruyunAuthError(code=code, message=data.get("msg", ""), path=path)
            raise KeruyunAPIError(code=code, message=data.get("msg", ""), path=path)

        return data.get("result")

    def get_store_list(self, brand_id: int) -> list[dict]:
        """
        Query all stores belonging to a brand.

        POST /open/standard/shop/MerchantOrgReadService.queryBrandStores

        Uses **brand-level** authorization.

        Args:
            brand_id: Brand ID.

        Returns:
            Dict with "shops" key containing list of store dicts.
        """
        return self._request(
            "/open/standard/shop/MerchantOrgReadService.queryBrandStores",
            body={},
            brand_id=brand_id,
        )

    def get_store_detail(self, shop_id: int) -> dict:
        """
        Query detailed information for a single store.

        POST /open/standard/shop/MerchantOrgReadService/queryById

        Uses **shop-level** authorization (shopIdenty only, no brandId).

        Args:
            shop_id: Shop ID to query.

        Returns:
            Store detail dict.
        """
        return self._request(
            "/open/standard/shop/MerchantOrgReadService/queryById",
            body={"shopId": shop_id},
            shop_id=shop_id,
        )
