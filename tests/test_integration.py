"""Integration tests against real Keruyun API.

Run with: pytest -m integration -v
Requires: credentials/keruyun.txt in smart-dining root
"""
import os
import pytest
from pathlib import Path
from keruyun.client import KeruyunClient

# Read credentials from smart-dining credentials directory
CRED_FILE = Path(__file__).parent.parent.parent.parent / "credentials" / "keruyun.txt"


def _load_creds():
    if not CRED_FILE.exists():
        return None
    text = CRED_FILE.read_text()
    creds = {}
    for line in text.strip().split('\n'):
        if ' ' in line and not line.startswith('#'):
            parts = line.split(' ', 1)
            if len(parts) == 2:
                creds[parts[0]] = parts[1].strip()
    return creds


CREDS = _load_creds()
SKIP = CREDS is None


@pytest.mark.integration
@pytest.mark.skipif(SKIP, reason="No credentials file found at credentials/keruyun.txt")
class TestIntegration:
    @pytest.fixture
    def client(self):
        return KeruyunClient(
            app_key=CREDS.get('AppKey', ''),
            app_secret=CREDS.get('AppSecret', ''),
        )

    @pytest.fixture
    def brand_id(self):
        return int(CREDS.get('品牌ID', '0'))

    def test_token_fetch(self, client, brand_id):
        """Verify token can be fetched from real API."""
        token = client._get_token(brand_id=brand_id, shop_id=None)
        assert token
        assert len(token) > 10

    def test_store_list(self, client, brand_id):
        """Verify store list can be fetched and contains expected fields."""
        result = client.shop.get_store_list(brand_id=brand_id)
        assert 'shops' in result
        assert len(result['shops']) > 0
        shop = result['shops'][0]
        assert 'shopId' in shop
        assert 'name' in shop
