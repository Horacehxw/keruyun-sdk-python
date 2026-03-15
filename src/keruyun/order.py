"""OrderAPI — order-related endpoints for the Keruyun open platform.

Note: Order endpoints require **shop-level** authorization (shopIdenty).
The brandId and shopIdenty parameters cannot coexist in the same request.
Date format for order queries is "YYYY-MM-DD HH:mm:ss" strings (not ms timestamps).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from keruyun.client import KeruyunClient


class OrderAPI:
    """Namespace for order-related API endpoints."""

    def __init__(self, client: KeruyunClient) -> None:
        self._client = client

    def get_order_list(
        self,
        shop_id: int,
        start_date: str,
        end_date: str,
        date_type: str = "1",
        order_types: list[int] | None = None,
        order_statuses: list[int] | None = None,
        page_num: int = 1,
        page_size: int = 100,
    ) -> Any:
        """
        Query a list of orders.

        POST /open/standard/order/queryList

        This is a **shop-level** API — requires shopIdenty, not brandId.

        Args:
            shop_id: Shop ID (used for auth via shopIdenty).
            start_date: Start datetime string (e.g. "2026-03-01 00:00:00").
            end_date: End datetime string (e.g. "2026-03-15 23:59:59").
            date_type: Date filter type ("1" = order date, default).
            order_types: Optional list of order type codes to filter.
            order_statuses: Optional list of order status codes to filter.
            page_num: Page number (1-indexed, default 1).
            page_size: Number of records per page (default 100).

        Returns:
            Parsed result dict (the "result" field of the API response).
        """
        body: dict[str, Any] = {
            "shopIds": [shop_id],
            "startDate": start_date,
            "endDate": end_date,
            "dateType": date_type,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        if order_types is not None:
            body["orderTypes"] = order_types
        if order_statuses is not None:
            body["orderStatuses"] = order_statuses

        return self._client._request(
            "/open/standard/order/queryList",
            body=body,
            shop_id=shop_id,
        )

    def get_order_detail(
        self,
        shop_id: int,
        order_id: str,
    ) -> Any:
        """
        Query details of a single order.

        POST /open/standard/order/queryDetail

        This is a **shop-level** API — requires shopIdenty, not brandId.

        Args:
            shop_id: Shop ID (used for auth via shopIdenty).
            order_id: Order ID string.

        Returns:
            Parsed result dict (the "result" field of the API response).
        """
        body: dict[str, Any] = {
            "orderId": order_id,
        }
        return self._client._request(
            "/open/standard/order/queryDetail",
            body=body,
            shop_id=shop_id,
        )
