"""
Tests for OrderAPI — order list and detail endpoints.

Uses the `responses` library to mock HTTP calls without real network requests.
"""

import pytest
import responses

from keruyun.client import KeruyunClient

BASE_URL = "https://openapi.keruyun.com"
BRAND_ID = 32296
SHOP_ID = 810094


@pytest.fixture
def client():
    c = KeruyunClient(app_key="testkey", app_secret="testsecret")
    # Pre-populate token cache with a brand-level token (tuple key matches client internals)
    c._tokens[(BRAND_ID, None)] = "cached_token"
    return c


class TestOrderAPI:
    @responses.activate
    def test_get_order_list(self, client):
        """POST /open/standard/order/queryList returns order list."""
        responses.add(
            responses.POST,
            f"{BASE_URL}/open/standard/order/queryList",
            json={
                "code": 0,
                "msg": "success",
                "result": {"list": [{"orderId": "ORD001", "saleAmt": 2500}]},
            },
        )
        result = client.order.get_order_list(
            brand_id=BRAND_ID,
            shop_ids=[SHOP_ID],
            start_date="2026-03-01",
            end_date="2026-03-15",
        )
        assert result["list"][0]["orderId"] == "ORD001"
        assert result["list"][0]["saleAmt"] == 2500

    @responses.activate
    def test_get_order_list_optional_params(self, client):
        """get_order_list sends optional order_types and order_statuses when provided."""
        responses.add(
            responses.POST,
            f"{BASE_URL}/open/standard/order/queryList",
            json={
                "code": 0,
                "msg": "success",
                "result": {"list": [], "total": 0},
            },
        )
        result = client.order.get_order_list(
            brand_id=BRAND_ID,
            shop_ids=[SHOP_ID],
            start_date="2026-03-01",
            end_date="2026-03-15",
            date_type="2",
            order_types=[1, 2],
            order_statuses=[3],
            page_num=2,
            page_size=50,
        )
        assert result["total"] == 0
        # Verify request body was sent
        import json
        sent_body = json.loads(responses.calls[0].request.body)
        assert sent_body["orderTypes"] == [1, 2]
        assert sent_body["orderStatuses"] == [3]
        assert sent_body["pageNum"] == 2
        assert sent_body["pageSize"] == 50
        assert sent_body["dateType"] == "2"

    @responses.activate
    def test_get_order_detail(self, client):
        """POST /open/standard/order/queryDetail returns order detail."""
        responses.add(
            responses.POST,
            f"{BASE_URL}/open/standard/order/queryDetail",
            json={
                "code": 0,
                "msg": "success",
                "result": {"orderId": "ORD001", "items": [{"name": "酸辣粉"}]},
            },
        )
        result = client.order.get_order_detail(brand_id=BRAND_ID, order_id="ORD001")
        assert result["orderId"] == "ORD001"
        assert result["items"][0]["name"] == "酸辣粉"

    @responses.activate
    def test_get_order_detail_sends_order_id(self, client):
        """get_order_detail includes orderId in the POST body."""
        responses.add(
            responses.POST,
            f"{BASE_URL}/open/standard/order/queryDetail",
            json={"code": 0, "msg": "success", "result": {"orderId": "ORD999"}},
        )
        client.order.get_order_detail(brand_id=BRAND_ID, order_id="ORD999")

        import json
        sent_body = json.loads(responses.calls[0].request.body)
        assert sent_body["orderId"] == "ORD999"
