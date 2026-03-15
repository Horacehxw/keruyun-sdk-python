"""
SupplyAPI — supply chain endpoints for the Keruyun open platform.

Covers inventory, BOM, goods, stock in/out, gross profit,
and procurement prediction endpoints.

Notes on authorization:
- Brand-level: get_inventory, get_bom, get_bom_schemes, get_goods_list,
  get_stock_in_out, get_gross_profit
- Shop-level: predict_by_thousand, predict_by_sales_plan
  (These require the "purchase" solution authorization per-shop.)
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

        Note: This endpoint may return error code 22000 (server error)
        if the supply chain module is not fully activated for the brand.

        Args:
            brand_id: Brand ID.
            org_id: Organisation/shop ID to filter by.
            page_num: Page number (1-based).
            page_size: Records per page.

        Returns:
            Parsed ``result`` field from the API response.
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

    def get_bom_schemes(self, brand_id: int) -> Any:
        """
        Query all BOM (cost card) schemes and their associated stores.

        POST /open/standard/supply/bom/queryAllBomSchemeWithStore

        Use the returned scheme ID as input to ``get_bom()``.

        Args:
            brand_id: Brand ID.

        Returns:
            Parsed ``result`` field containing list of BOM schemes with
            ``id``, ``name``, ``relatedStoreIds``, ``tenantId``.
        """
        return self._client._request(
            "/open/standard/supply/bom/queryAllBomSchemeWithStore",
            body={},
            brand_id=brand_id,
        )

    def get_bom(
        self,
        brand_id: int,
        bom_scheme_id: str,
        page_num: int = 1,
        page_size: int = 50,
    ) -> Any:
        """
        Query Bill-of-Materials (BOM) records.

        POST /open/standard/supply/bom/pageQueryBom

        Use ``get_bom_schemes()`` first to obtain valid ``bom_scheme_id`` values.

        Args:
            brand_id: Brand ID.
            bom_scheme_id: BOM scheme UUID (from get_bom_schemes).
            page_num: Page number (1-based).
            page_size: Records per page.

        Returns:
            Parsed ``result`` field from the API response.
        """
        body: dict[str, Any] = {
            "bomSchemeId": bom_scheme_id,
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
        keyword: str | None = None,
    ) -> Any:
        """
        Query supply goods list with pagination.

        POST /open/standard/supply/goods/findListForPage

        Args:
            brand_id: Brand ID.
            page_num: Page number (1-based).
            page_size: Records per page.
            keyword: Optional search keyword.

        Returns:
            Parsed ``result`` field from the API response.
        """
        body: dict[str, Any] = {
            "pageNum": page_num,
            "pageSize": page_size,
        }
        if keyword is not None:
            body["keyword"] = keyword
        return self._client._request(
            "/open/standard/supply/goods/findListForPage",
            body=body,
            brand_id=brand_id,
        )

    def get_stock_in_out(
        self,
        brand_id: int,
        org_ids: list[int],
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
            org_ids: List of organisation/shop IDs to filter.
            start_date: Report start date (``YYYY-MM-DD``).
            end_date: Report end date (``YYYY-MM-DD``).
            page_num: Page number (1-based).
            page_size: Records per page.

        Returns:
            Parsed ``result`` field from the API response.
        """
        body: dict[str, Any] = {
            "orgIds": org_ids,
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

    def get_gross_profit(
        self,
        brand_id: int,
        org_id_list: list[int],
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
            org_id_list: List of organisation/shop IDs to filter.
            start_date: Report start date (``YYYY-MM-DD``).
            end_date: Report end date (``YYYY-MM-DD``).
            page_num: Page number (1-based).
            page_size: Records per page.

        Returns:
            Parsed ``result`` field from the API response.
        """
        body: dict[str, Any] = {
            "orgIdList": org_id_list,
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
    # Shop-level methods (require per-shop "purchase" authorization)
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

        Note: Requires the "purchase" solution authorization for this shop.
        Returns error code 1002 if not authorized.

        Args:
            shop_id: Shop ID.
            refer_start: Historical reference period start date (``YYYY-MM-DD``).
            refer_end: Historical reference period end date (``YYYY-MM-DD``).
            predict_start: Prediction period start date (``YYYY-MM-DD``).
            predict_end: Prediction period end date (``YYYY-MM-DD``).

        Returns:
            Parsed ``result`` field from the API response.
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

        Note: Requires the "purchase" solution authorization for this shop.
        Returns error code 1002 if not authorized.

        Args:
            shop_id: Shop ID.
            predict_start: Prediction period start date (``YYYY-MM-DD``).
            predict_end: Prediction period end date (``YYYY-MM-DD``).

        Returns:
            Parsed ``result`` field from the API response.
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
