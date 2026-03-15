"""
Tests for SupplyAPI — supply chain endpoints.

Uses the ``responses`` library to mock HTTP calls without real network requests.
Tokens are pre-seeded in ``_tokens`` cache to skip token-fetch calls.
"""

import pytest
import responses as responses_lib

from keruyun import KeruyunClient

BASE_URL = "https://openapi.keruyun.com"
BRAND_ID = 32296
SHOP_ID = 810094
APP_KEY = "testkey"
APP_SECRET = "testsecret"
CACHED_TOKEN = "cached_token"


def _make_api_response(result, code: int = 0, msg: str = "success"):
    """Real API returns {"code": 0, "result": {...}}"""
    return {"code": code, "msg": msg, "result": result}


@pytest.fixture
def brand_client():
    """KeruyunClient with a pre-cached brand-level token (skips token HTTP call)."""
    c = KeruyunClient(app_key=APP_KEY, app_secret=APP_SECRET, base_url=BASE_URL)
    c._tokens[(BRAND_ID, None)] = CACHED_TOKEN
    return c


@pytest.fixture
def shop_client():
    """KeruyunClient with a pre-cached shop-level token (skips token HTTP call)."""
    c = KeruyunClient(app_key=APP_KEY, app_secret=APP_SECRET, base_url=BASE_URL)
    c._tokens[(None, SHOP_ID)] = CACHED_TOKEN
    return c


# ---------------------------------------------------------------------------
# Brand-level endpoint tests
# ---------------------------------------------------------------------------


@responses_lib.activate
def test_get_inventory(brand_client):
    """POST /open/standard/supply/stock/goods/findByCondition returns inventory data."""
    path = "/open/standard/supply/stock/goods/findByCondition"
    mock_data = {"list": [{"goodsId": 1, "stockQty": 50}], "total": 1}
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + path,
        json=_make_api_response(mock_data),
        status=200,
    )

    result = brand_client.supply.get_inventory(
        brand_id=BRAND_ID, org_id=999, page_num=1, page_size=50
    )

    assert result == mock_data
    assert len(responses_lib.calls) == 1
    req = responses_lib.calls[0].request
    assert path in req.url
    assert "brandId=" in req.url
    assert b"orgId" in req.body


@responses_lib.activate
def test_get_bom(brand_client):
    """POST /open/standard/supply/bom/pageQueryBom returns BOM data."""
    path = "/open/standard/supply/bom/pageQueryBom"
    mock_data = {"list": [{"bomId": 10, "name": "soup-base"}], "total": 1}
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + path,
        json=_make_api_response(mock_data),
        status=200,
    )

    result = brand_client.supply.get_bom(brand_id=BRAND_ID, page_num=1, page_size=20)

    assert result == mock_data
    assert len(responses_lib.calls) == 1
    req = responses_lib.calls[0].request
    assert path in req.url
    assert "brandId=" in req.url


@responses_lib.activate
def test_get_goods_list(brand_client):
    """POST /open/standard/supply/goods/findListForPage returns goods list."""
    path = "/open/standard/supply/goods/findListForPage"
    mock_data = {"list": [{"goodsId": 42, "goodsName": "beef"}], "total": 1}
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + path,
        json=_make_api_response(mock_data),
        status=200,
    )

    result = brand_client.supply.get_goods_list(
        brand_id=BRAND_ID, page_num=2, page_size=100
    )

    assert result == mock_data
    assert len(responses_lib.calls) == 1
    req = responses_lib.calls[0].request
    assert path in req.url
    assert b"pageNum" in req.body
    assert b"pageSize" in req.body


@responses_lib.activate
def test_get_stock_in_out(brand_client):
    """POST /open/standard/supply/stock/report/stockInOutDetail returns stock report."""
    path = "/open/standard/supply/stock/report/stockInOutDetail"
    mock_data = {"list": [{"inQty": 100, "outQty": 30}], "total": 1}
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + path,
        json=_make_api_response(mock_data),
        status=200,
    )

    result = brand_client.supply.get_stock_in_out(
        brand_id=BRAND_ID,
        start_date="2026-01-01",
        end_date="2026-01-31",
        page_num=1,
        page_size=100,
    )

    assert result == mock_data
    assert len(responses_lib.calls) == 1
    req = responses_lib.calls[0].request
    assert path in req.url
    assert b"startDate" in req.body
    assert b"endDate" in req.body


@responses_lib.activate
def test_get_purchase_in_list(brand_client):
    """POST /open/standard/procurement/supply/purchase/in/list returns purchase records."""
    path = "/open/standard/procurement/supply/purchase/in/list"
    mock_data = {"list": [{"purchaseId": 7, "amount": 500.0}], "total": 1}
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + path,
        json=_make_api_response(mock_data),
        status=200,
    )

    result = brand_client.supply.get_purchase_in_list(
        brand_id=BRAND_ID,
        start_date="2026-01-01",
        end_date="2026-01-31",
    )

    assert result == mock_data
    assert len(responses_lib.calls) == 1
    req = responses_lib.calls[0].request
    assert path in req.url
    assert b"startDate" in req.body
    assert b"endDate" in req.body


@responses_lib.activate
def test_get_gross_profit(brand_client):
    """POST /open/standard/supply/profit/report/listDishGrossProfit returns profit data."""
    path = "/open/standard/supply/profit/report/listDishGrossProfit"
    mock_data = {"list": [{"dishName": "noodle", "grossProfit": 120.5}], "total": 1}
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + path,
        json=_make_api_response(mock_data),
        status=200,
    )

    result = brand_client.supply.get_gross_profit(
        brand_id=BRAND_ID,
        start_date="2026-01-01",
        end_date="2026-01-31",
        page_num=1,
        page_size=50,
    )

    assert result == mock_data
    assert len(responses_lib.calls) == 1
    req = responses_lib.calls[0].request
    assert path in req.url
    assert b"startDate" in req.body
    assert b"endDate" in req.body


# ---------------------------------------------------------------------------
# Shop-level endpoint tests
# ---------------------------------------------------------------------------


@responses_lib.activate
def test_predict_by_thousand(shop_client):
    """POST /open/standard/purchase/thousand/predictbill returns prediction bill."""
    path = "/open/standard/purchase/thousand/predictbill"
    mock_data = {"billId": "PRED-001", "items": [{"goodsName": "broth", "qty": 20}]}
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + path,
        json=_make_api_response(mock_data),
        status=200,
    )

    result = shop_client.supply.predict_by_thousand(
        shop_id=SHOP_ID,
        refer_start="2026-01-01",
        refer_end="2026-01-14",
        predict_start="2026-01-15",
        predict_end="2026-01-21",
    )

    assert result == mock_data
    assert len(responses_lib.calls) == 1
    req = responses_lib.calls[0].request
    assert path in req.url
    assert "shopIdenty=" in req.url
    assert b"referStart" in req.body
    assert b"referEnd" in req.body
    assert b"predictStart" in req.body
    assert b"predictEnd" in req.body


@responses_lib.activate
def test_predict_by_sales_plan(shop_client):
    """POST /open/standard/purchase/commoditysalesplan/apply returns plan-based prediction."""
    path = "/open/standard/purchase/commoditysalesplan/apply"
    mock_data = {"planId": "PLAN-999", "items": [{"goodsName": "noodle", "qty": 100}]}
    responses_lib.add(
        responses_lib.POST,
        BASE_URL + path,
        json=_make_api_response(mock_data),
        status=200,
    )

    result = shop_client.supply.predict_by_sales_plan(
        shop_id=SHOP_ID,
        predict_start="2026-01-15",
        predict_end="2026-01-21",
    )

    assert result == mock_data
    assert len(responses_lib.calls) == 1
    req = responses_lib.calls[0].request
    assert path in req.url
    assert "shopIdenty=" in req.url
    assert b"predictStart" in req.body
    assert b"predictEnd" in req.body
