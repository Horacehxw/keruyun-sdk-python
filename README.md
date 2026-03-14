# keruyun-sdk-python

Python SDK for the Keruyun (客如云) restaurant POS open platform API.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```python
from keruyun import KeruyunClient

client = KeruyunClient(
    app_key="your_app_key",
    app_secret="your_app_secret",
)

# Fetch brand-level data
result = client.report.get_daily_flow(brand_id=32296, date="2026-03-15")

# Fetch shop-level data
result = client.report.get_shop_flow(shop_id=810094, date="2026-03-15")
```

## Running Tests

```bash
pytest -v
```
