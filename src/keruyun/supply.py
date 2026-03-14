"""
SupplyAPI — supply chain endpoints for the Keruyun open platform.

Covers inventory, BOM, goods, stock in/out, purchase, gross profit,
and procurement prediction endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from keruyun.client import KeruyunClient


class SupplyAPI:
    """Supply chain API namespace attached to KeruyunClient as ``client.supply``."""

    def __init__(self, client: KeruyunClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Brand-level methods
    # ------------------------------------------------------------------

    def get_inventory(
        self,
        brand_id: int,
        org_id: int,
        page_num: int = 1,
        page_size: int = 100,
    ) -> Any:
        """
        Query inventory stock levels by condition.

        POST /open/standard/supply/stock/goods/findByCondition

        Args:
            brand_id: Brand ID.
            org_id: Organisation ID to filter by.
            page_num: Page number (1-based).
            page_size: Records per page.

        Returns:
            Parsed ``data`` field from the API response.
        """
        body: dict[str, Any] = {
            "orgId": org_id,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        return self._client._request(
            "/open/standard/supply/stock/goods/findByCondition",
            body=body,
            brand_id=brand_id,
        )

    def get_bom(
        self,
        brand_id: int,
        page_num: int = 1,
        page_size: int = 100,
    ) -> Any:
        """
        Query Bill-of-Materials (BOM) records.

        POST /open/standard/supply/bom/pageQueryBom

        Args:
            brand_id: Brand ID.
            page_num: Page number (1-based).
            page_size: Records per page.

        Returns:
            Parsed ``data`` field from the API response.
        """
        body: dict[str, Any] = {
            "pageNum": page_num,
            "pageSize": page_size,
        }
        return self._client._request(
            "/open/standard/supply/bom/pageQueryBom",
            body=body,
            brand_id=brand_id,
        )

    def get_goods_list(
        self,
        brand_id: int,
        page_num: int = 1,
        page_size: int = 100,
    ) -> Any:
        """
        Query supply goods list with pagination.

        POST /open/standard/supply/goods/findListForPage

        Args:
            brand_id: Brand ID.
            page_num: Page number (1-based).
            page_size: Records per page.

        Returns:
            Parsed ``data`` field from the API response.
        """
        body: dict[str, Any] = {
            "pageNum": page_num,
            "pageSize": page_size,
        }
        return self._client._request(
            "/open/standard/supply/goods/findListForPage",
            body=body,
            brand_id=brand_id,
        )

    def get_stock_in_out(
        self,
        brand_id: int,
        start_date: str,
        end_date: str,
        page_num: int = 1,
        page_size: int = 100,
    ) -> Any:
        """
        Query stock-in/stock-out detail report.

        POST /open/standard/supply/stock/report/stockInOutDetail

        Args:
            brand_id: Brand ID.
            start_date: Report start date (``YYYY-MM-DD``).
            end_date: Report end date (``YYYY-MM-DD``).
            page_num: Page number (1-based).
            page_size: Records per page.

        Returns:
            Parsed ``data`` field from the API response.
        """
        body: dict[str, Any] = {
            "startDate": start_date,
            "endDate": end_date,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        return self._client._request(
            "/open/standard/supply/stock/report/stockInOutDetail",
            body=body,
            brand_id=brand_id,
        )

    def get_purchase_in_list(
        self,
        brand_id: int,
        start_date: str,
        end_date: str,
        page_num: int = 1,
        page_size: int = 100,
    ) -> Any:
        """
        Query procurement purchase-in list.

        POST /open/standard/procurement/supply/purchase/in/list

        Args:
            brand_id: Brand ID.
            start_date: Report start date (``YYYY-MM-DD``).
            end_date: Report end date (``YYYY-MM-DD``).
            page_num: Page number (1-based).
            page_size: Records per page.

        Returns:
            Parsed ``data`` field from the API response.
        """
        body: dict[str, Any] = {
            "startDate": start_date,
            "endDate": end_date,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        return self._client._request(
            "/open/standard/procurement/supply/purchase/in/list",
            body=body,
            brand_id=brand_id,
        )

    def get_gross_profit(
        self,
        brand_id: int,
        start_date: str,
        end_date: str,
        page_num: int = 1,
        page_size: int = 100,
    ) -> Any:
        """
        Query dish gross profit report.

        POST /open/standard/supply/profit/report/listDishGrossProfit

        Args:
            brand_id: Brand ID.
            start_date: Report start date (``YYYY-MM-DD``).
            end_date: Report end date (``YYYY-MM-DD``).
            page_num: Page number (1-based).
            page_size: Records per page.

        Returns:
            Parsed ``data`` field from the API response.
        """
        body: dict[str, Any] = {
            "startDate": start_date,
            "endDate": end_date,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        return self._client._request(
            "/open/standard/supply/profit/report/listDishGrossProfit",
            body=body,
            brand_id=brand_id,
        )

    # ------------------------------------------------------------------
    # Shop-level methods
    # ------------------------------------------------------------------

    def predict_by_thousand(
        self,
        shop_id: int,
        refer_start: str,
        refer_end: str,
        predict_start: str,
        predict_end: str,
    ) -> Any:
        """
        Generate procurement prediction based on thousand-table model.

        POST /open/standard/purchase/thousand/predictbill

        Args:
            shop_id: Shop ID.
            refer_start: Historical reference period start date (``YYYY-MM-DD``).
            refer_end: Historical reference period end date (``YYYY-MM-DD``).
            predict_start: Prediction period start date (``YYYY-MM-DD``).
            predict_end: Prediction period end date (``YYYY-MM-DD``).

        Returns:
            Parsed ``data`` field from the API response.
        """
        body: dict[str, Any] = {
            "referStart": refer_start,
            "referEnd": refer_end,
            "predictStart": predict_start,
            "predictEnd": predict_end,
        }
        return self._client._request(
            "/open/standard/purchase/thousand/predictbill",
            body=body,
            shop_id=shop_id,
        )

    def predict_by_sales_plan(
        self,
        shop_id: int,
        predict_start: str,
        predict_end: str,
    ) -> Any:
        """
        Generate procurement prediction based on commodity sales plan.

        POST /open/standard/purchase/commoditysalesplan/apply

        Args:
            shop_id: Shop ID.
            predict_start: Prediction period start date (``YYYY-MM-DD``).
            predict_end: Prediction period end date (``YYYY-MM-DD``).

        Returns:
            Parsed ``data`` field from the API response.
        """
        body: dict[str, Any] = {
            "predictStart": predict_start,
            "predictEnd": predict_end,
        }
        return self._client._request(
            "/open/standard/purchase/commoditysalesplan/apply",
            body=body,
            shop_id=shop_id,
        )
