# keruyun-sdk-python

Python SDK for the [Keruyun (客如云)](https://open.keruyun.com/) restaurant POS open platform API.

> **Disclaimer:** This is an unofficial, community-maintained SDK. 客如云 is a trademark of Beijing Keruyun Technology Co., Ltd. This project is not affiliated with or endorsed by Keruyun.

## Features

- **Report** — daily revenue, menu sales, payment breakdown, shop-level flow
- **Shop** — store list and detail queries
- **Order** — order list and detail lookups
- **Supply** — inventory, BOM, procurement prediction, and more (8 endpoints)
- Automatic token management and caching
- SHA256 request signing per Keruyun spec

## Installation

```bash
pip install git+https://github.com/Horacehxw/keruyun-sdk-python.git
```

For development:

```bash
git clone https://github.com/Horacehxw/keruyun-sdk-python.git
cd keruyun-sdk-python
pip install -e ".[dev]"
```

## Quick Start

```python
from keruyun import KeruyunClient

client = KeruyunClient(
    app_key="your_app_key",
    app_secret="your_app_secret",
)

# Brand-level daily report
result = client.report.get_daily_flow(brand_id=YOUR_BRAND_ID, date="2026-03-15")

# Shop-level data
result = client.report.get_shop_flow(shop_id=YOUR_SHOP_ID, date="2026-03-15")

# Store list
shops = client.shop.get_shop_list(brand_id=YOUR_BRAND_ID)

# Supply chain - inventory
inventory = client.supply.get_inventory(brand_id=YOUR_BRAND_ID, shop_id=YOUR_SHOP_ID)
```

You'll need API credentials from the [Keruyun Open Platform](https://open.keruyun.com/).

## API Modules

| Module | Endpoints | Description |
|--------|-----------|-------------|
| `report` | 5 | Revenue, menu sales, payment stats |
| `shop` | 2 | Store list and detail |
| `order` | 2 | Order list and detail |
| `supply` | 8 | Inventory, BOM, procurement |

## Testing

```bash
# Unit tests (no API key needed)
pytest -v

# Integration tests (requires real credentials)
pytest -v -m integration
```

## License

[MIT](LICENSE)
