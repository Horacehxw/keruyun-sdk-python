"""
Tests for ShopAPI — store list and store detail endpoints.

Uses the `responses` library to mock HTTP calls without making real network requests.
"""

import pytest
import responses
from keruyun.client import KeruyunClient

BASE_URL = "https://openapi.keruyun.com"


@pytest.fixture
def client():
    c = KeruyunClient(app_key="testkey", app_secret="testsecret")
    # Pre-populate token cache with brand-level token (cache key is (brand_id, shop_id))
    c._tokens[(32296, None)] = "cached_token"
    c._tokens[(None, 810094)] = "cached_shop_token"
    return c


class TestShopAPI:
    @responses.activate
    def test_get_store_list(self, client):
        responses.post(
            f"{BASE_URL}/open/standard/shop/MerchantOrgReadService.queryBrandStores",
            json={"code": 0, "result": [{"shopId": 810094, "shopName": "人和店"}]},
        )
        result = client.shop.get_store_list(brand_id=32296)
        assert result[0]["shopName"] == "人和店"

    @responses.activate
    def test_get_store_detail(self, client):
        """get_store_detail uses shop-level auth (shopIdenty only, no brandId)."""
        responses.post(
            f"{BASE_URL}/open/standard/shop/MerchantOrgReadService/queryById",
            json={"code": 0, "result": {"shopId": 810094, "shopName": "人和店", "address": "重庆市"}},
        )
        result = client.shop.get_store_detail(shop_id=810094)
        assert result["shopId"] == 810094
