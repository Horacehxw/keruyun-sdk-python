"""
ReportAPI — report/analytics endpoints for the Keruyun open platform.

All methods POST to standard report paths, passing shop IDs, a date range,
and optional pagination. The response `result` field is returned directly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from keruyun.client import KeruyunClient


class ReportAPI:
    """Namespace for Keruyun report/analytics endpoints."""

    def __init__(self, client: KeruyunClient) -> None:
        self._client = client

    def _build_body(
        self,
        shop_ids: list[int],
        start_date: int,
        end_date: int,
        page_num: int = 1,
        page_size: int = 50,
    ) -> dict:
        """Build the common request body shared by all report endpoints."""
        return {
            "shopIds": shop_ids,
            "dateRange": {
                "dateType": "BUSI_DATE",
                "startDate": start_date,
                "endDate": end_date,
            },
            "pageBean": {
                "pageNum": page_num,
                "pageSize": page_size,
            },
        }

    def _request(self, path: str, body: dict, brand_id: int) -> Any:
        """
        POST to a standard report endpoint and return the ``result`` field.

        Standard report APIs use ``result`` as the top-level data key instead
        of the ``data`` key used by other Keruyun endpoints.
        """
        # _client._request returns data.get("data"); we need data.get("result")
        # so we bypass the high-level helper and replicate the request cycle,
        # but extract "result" instead.
        import json
        from keruyun.signing import compute_sign
        from keruyun.exceptions import KeruyunAPIError, KeruyunAuthError

        _AUTH_ERROR_CODES = {100, 101, 102, 103, 104, 105, 106, 107, 108}

        def _do(allow_retry: bool) -> Any:
            body_json = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
            params = self._client._build_query_params(brand_id=brand_id, shop_id=None)
            sign = compute_sign(params, body_json=body_json, token_or_secret=params["token"])
            params["sign"] = sign

            url = self._client._base_url + path
            resp = self._client._session.post(
                url,
                params=params,
                data=body_json.encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()

            code = data.get("code", 0)
            if code != 0:
                if code in _AUTH_ERROR_CODES:
                    self._client._tokens.pop((brand_id, None), None)
                    if allow_retry:
                        return _do(allow_retry=False)
                    raise KeruyunAuthError(code=code, message=data.get("msg", ""), path=path)
                raise KeruyunAPIError(code=code, message=data.get("msg", ""), path=path)

            return data.get("result")

        return _do(allow_retry=True)

    def get_business_income(
        self,
        brand_id: int,
        shop_ids: list[int],
        start_date: int,
        end_date: int,
        page_num: int = 1,
        page_size: int = 50,
        coupon_statistical_type: str = "BY_NAME",
        store_statistical_type: str = "COMBINE",
        org_statistics_type: str = "BY_SHOP",
        period_type: str = "BY_DAY",
        order_source_list: list[str] | None = None,
        order_type_list: list[str] | None = None,
        statistics_by_shop: bool = True,
    ) -> Any:
        """
        Fetch business income summary report.

        POST /open/standard/report/business/income/v3/list

        Args:
            brand_id: Brand ID.
            shop_ids: List of shop IDs to query.
            start_date: Start timestamp in milliseconds (BUSI_DATE).
            end_date: End timestamp in milliseconds (BUSI_DATE).
            page_num: Page number (default 1).
            page_size: Page size (default 50).
            coupon_statistical_type: Coupon stat type (default "BY_NAME").
            store_statistical_type: Store stat type (default "COMBINE").
            org_statistics_type: Org statistics type (default "BY_SHOP").
            period_type: Period grouping type (default "BY_DAY").
            order_source_list: Order sources (default ["POS"]).
            order_type_list: Order types (default ["FOR_HERE"]).
            statistics_by_shop: Whether to split stats by shop (default True).

        Returns:
            The ``result`` field from the API response.
        """
        if order_source_list is None:
            order_source_list = ["POS"]
        if order_type_list is None:
            order_type_list = ["FOR_HERE"]
        body = self._build_body(shop_ids, start_date, end_date, page_num, page_size)
        body.update({
            "couponStatisticalType": coupon_statistical_type,
            "storeStatisticalType": store_statistical_type,
            "orgStatisticsType": org_statistics_type,
            "periodType": period_type,
            "orderSourceList": order_source_list,
            "orderTypeList": order_type_list,
            "statisticsByShop": statistics_by_shop,
        })
        return self._request(
            path="/open/standard/report/business/income/v3/list",
            body=body,
            brand_id=brand_id,
        )

    def get_income_constitute(
        self,
        brand_id: int,
        shop_ids: list[int],
        start_date: int,
        end_date: int,
        page_num: int = 1,
        page_size: int = 50,
        coupon_statistical_type: str = "BY_NAME",
        store_statistical_type: str = "COMBINE",
        org_statistics_type: str = "BY_SHOP",
        period_type: str = "BY_DAY",
        order_source_list: list[str] | None = None,
        order_type_list: list[str] | None = None,
        statistics_by_shop: bool = True,
    ) -> Any:
        """
        Fetch income constitution breakdown (dine-in, takeout, etc.).

        POST /open/standard/report/business/income/constitute/v3/list

        Note: Date range must be at most 1 day.

        Args:
            brand_id: Brand ID.
            shop_ids: List of shop IDs to query.
            start_date: Start timestamp in milliseconds.
            end_date: End timestamp in milliseconds.
            page_num: Page number (default 1).
            page_size: Page size (default 50).
            coupon_statistical_type: Coupon stat type (default "BY_NAME").
            store_statistical_type: Store stat type (default "COMBINE").
            org_statistics_type: Org statistics type (default "BY_SHOP").
            period_type: Period grouping type (default "BY_DAY").
            order_source_list: Order sources (default ["POS"]).
            order_type_list: Order types (default ["FOR_HERE"]).
            statistics_by_shop: Whether to split stats by shop (default True).

        Returns:
            The ``result`` field from the API response.
        """
        if order_source_list is None:
            order_source_list = ["POS"]
        if order_type_list is None:
            order_type_list = ["FOR_HERE"]
        body = self._build_body(shop_ids, start_date, end_date, page_num, page_size)
        body.update({
            "couponStatisticalType": coupon_statistical_type,
            "storeStatisticalType": store_statistical_type,
            "orgStatisticsType": org_statistics_type,
            "periodType": period_type,
            "orderSourceList": order_source_list,
            "orderTypeList": order_type_list,
            "statisticsByShop": statistics_by_shop,
        })
        return self._request(
            path="/open/standard/report/business/income/constitute/v3/list",
            body=body,
            brand_id=brand_id,
        )

    def get_menu_sales(
        self,
        brand_id: int,
        shop_ids: list[int],
        start_date: int,
        end_date: int,
        page_num: int = 1,
        page_size: int = 50,
        count_collect_type: int = 1,
        sell_collect_type: bool = True,
        order_source_list: list[str] | None = None,
        order_type_list: list[str] | None = None,
        goods_temp_flag: int = 0,
        sales_type: str = "NORMAL",
        statistics_by_shop: bool = True,
        group_type: int = 1,
        org_statistics_type: str = "BY_SHOP",
        period_type: str = "BY_DAY",
        coupon_statistical_type: str = "BY_NAME",
        sort_field: str = "sellNum",
        sort_type: str = "DESC",
    ) -> Any:
        """
        Fetch menu item sales statistics.

        POST /open/standard/report/orderItem/list

        Note: Date range must be at most 1 day.

        Args:
            brand_id: Brand ID.
            shop_ids: List of shop IDs to query.
            start_date: Start timestamp in milliseconds.
            end_date: End timestamp in milliseconds.
            page_num: Page number (default 1).
            page_size: Page size (default 50).
            count_collect_type: Counting dimension (int, default 1).
            sell_collect_type: Sell aggregation type (bool, default True).
            order_source_list: Order sources (default ["POS"]).
            order_type_list: Order types (default ["FOR_HERE"]).
            goods_temp_flag: Temporary goods flag (int, default 0).
            sales_type: Sales type filter (default "NORMAL").
            statistics_by_shop: Split stats by shop (default True).
            group_type: Grouping type (int, default 1).
            org_statistics_type: Org statistics type (default "BY_SHOP").
            period_type: Period grouping type (default "BY_DAY").
            coupon_statistical_type: Coupon stat type (default "BY_NAME").
            sort_field: Sort field name (default "sellNum").
            sort_type: Sort direction (default "DESC").

        Returns:
            The ``result`` field from the API response.
        """
        if order_source_list is None:
            order_source_list = ["POS"]
        if order_type_list is None:
            order_type_list = ["FOR_HERE"]
        body = self._build_body(shop_ids, start_date, end_date, page_num, page_size)
        body.update({
            "countLatitude": {"countCollectType": count_collect_type},
            "sellLatitude": {"sellCollectType": sell_collect_type},
            "orderSourceCondition": {"orderSourceList": order_source_list},
            "orderTypeCondition": {"orderTypeList": order_type_list},
            "goodsTempFlag": goods_temp_flag,
            "salesType": sales_type,
            "statisticsByShop": statistics_by_shop,
            "groupType": group_type,
            "orgStatisticsType": org_statistics_type,
            "periodType": period_type,
            "couponStatisticalType": coupon_statistical_type,
            "sortField": sort_field,
            "sortType": sort_type,
        })
        return self._request(
            path="/open/standard/report/orderItem/list",
            body=body,
            brand_id=brand_id,
        )

    def get_payment_stats(
        self,
        brand_id: int,
        shop_ids: list[int],
        start_date: int,
        end_date: int,
        page_num: int = 1,
        page_size: int = 50,
    ) -> Any:
        """
        Fetch payment method statistics.

        POST /open/standard/report/paymethod/statistics

        Args:
            brand_id: Brand ID.
            shop_ids: List of shop IDs to query.
            start_date: Start timestamp in milliseconds.
            end_date: End timestamp in milliseconds.
            page_num: Page number (default 1).
            page_size: Page size (default 50).

        Returns:
            The ``result`` field from the API response.
        """
        body = self._build_body(shop_ids, start_date, end_date, page_num, page_size)
        return self._request(
            path="/open/standard/report/paymethod/statistics",
            body=body,
            brand_id=brand_id,
        )

    def get_promo_stats(
        self,
        brand_id: int,
        shop_ids: list[int],
        start_date: int,
        end_date: int,
        page_num: int = 1,
        page_size: int = 50,
        coupon_statistical_type: str = "BY_NAME",
        store_statistical_type: str = "COMBINE",
        org_statistics_type: str = "BY_SHOP",
        period_type: str = "BY_DAY",
        order_source_list: list[str] | None = None,
        order_type_list: list[str] | None = None,
        statistics_by_shop: bool = True,
    ) -> Any:
        """
        Fetch promotional discount statistics.

        POST /open/standard/report/business/income/promo/v3/list

        Note: Date range must be at most 1 day.

        Args:
            brand_id: Brand ID.
            shop_ids: List of shop IDs to query.
            start_date: Start timestamp in milliseconds.
            end_date: End timestamp in milliseconds.
            page_num: Page number (default 1).
            page_size: Page size (default 50).
            coupon_statistical_type: Coupon stat type (default "BY_NAME").
            store_statistical_type: Store stat type (default "COMBINE").
            org_statistics_type: Org statistics type (default "BY_SHOP").
            period_type: Period grouping type (default "BY_DAY").
            order_source_list: Order sources (default ["POS"]).
            order_type_list: Order types (default ["FOR_HERE"]).
            statistics_by_shop: Whether to split stats by shop (default True).

        Returns:
            The ``result`` field from the API response.
        """
        if order_source_list is None:
            order_source_list = ["POS"]
        if order_type_list is None:
            order_type_list = ["FOR_HERE"]
        body = self._build_body(shop_ids, start_date, end_date, page_num, page_size)
        body.update({
            "couponStatisticalType": coupon_statistical_type,
            "storeStatisticalType": store_statistical_type,
            "orgStatisticsType": org_statistics_type,
            "periodType": period_type,
            "orderSourceList": order_source_list,
            "orderTypeList": order_type_list,
            "statisticsByShop": statistics_by_shop,
        })
        return self._request(
            path="/open/standard/report/business/income/promo/v3/list",
            body=body,
            brand_id=brand_id,
        )
