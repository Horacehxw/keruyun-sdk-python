"""
Tests for ReportAPI — the 5 report endpoints.

Uses the `responses` library to mock HTTP calls without making real network requests.
Token is pre-seeded in the client cache to avoid token-fetch HTTP calls.
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
    # Pre-seed token cache with tuple key matching (brand_id, shop_id)
    c._tokens[(BRAND_ID, None)] = "cached_token"
    return c


class TestReportAPI:
    @responses.activate
    def test_get_business_income(self, client):
        responses.post(
            f"{BASE_URL}/open/standard/report/business/income/v3/list",
            json={"code": 0, "result": {"list": [{"saleAmt": "8500.00", "shopId": SHOP_ID}]}},
        )
        result = client.report.get_business_income(
            brand_id=BRAND_ID,
            shop_ids=[SHOP_ID],
            start_date=1710000000000,
            end_date=1710086400000,
        )
        assert result["list"][0]["saleAmt"] == "8500.00"

    @responses.activate
    def test_get_income_constitute(self, client):
        responses.post(
            f"{BASE_URL}/open/standard/report/business/income/constitute/v3/list",
            json={"code": 0, "result": {"list": [{"itemList": [{"code": "DINE_IN", "amount": "5000"}]}]}},
        )
        result = client.report.get_income_constitute(
            brand_id=BRAND_ID,
            shop_ids=[SHOP_ID],
            start_date=1710000000000,
            end_date=1710086400000,
        )
        assert "list" in result

    @responses.activate
    def test_get_menu_sales(self, client):
        # This endpoint returns code 2001 on success (not 0)
        responses.post(
            f"{BASE_URL}/open/standard/report/orderItem/list",
            json={"code": 2001, "result": {"list": [{"itemName": "酸辣粉", "quantity": 120}]}},
        )
        result = client.report.get_menu_sales(
            brand_id=BRAND_ID,
            shop_ids=[SHOP_ID],
            start_date=1710000000000,
            end_date=1710086400000,
        )
        assert result["list"][0]["itemName"] == "酸辣粉"

    @responses.activate
    def test_get_payment_stats(self, client):
        responses.post(
            f"{BASE_URL}/open/standard/report/paymethod/statistics",
            json={"code": 0, "result": {"list": [{"payMethod": "WECHAT", "amount": "3000"}]}},
        )
        result = client.report.get_payment_stats(
            brand_id=BRAND_ID,
            shop_ids=[SHOP_ID],
            start_date=1710000000000,
            end_date=1710086400000,
        )
        assert "list" in result

    @responses.activate
    def test_get_promo_stats(self, client):
        responses.post(
            f"{BASE_URL}/open/standard/report/business/income/promo/v3/list",
            json={"code": 0, "result": {"list": [{"promoType": "COUPON", "amount": "200"}]}},
        )
        result = client.report.get_promo_stats(
            brand_id=BRAND_ID,
            shop_ids=[SHOP_ID],
            start_date=1710000000000,
            end_date=1710086400000,
        )
        assert "list" in result
