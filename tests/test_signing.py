import hashlib
import pytest

from keruyun.signing import build_sign_string, compute_sign


class TestBuildSignString:
    def test_brand_auth_no_body(self):
        """Brand-level call without body: params concatenated in fixed order + token appended."""
        params = {
            "appKey": "testkey",
            "brandId": 32296,
            "timestamp": 1710000000,
            "version": "2.0",
        }
        result = build_sign_string(params, body_json=None, token_or_secret="mytoken")
        expected = "appKeytestkeybrandId32296timestamp1710000000version2.0mytoken"
        assert result == expected

    def test_shop_auth_with_body(self):
        """Shop-level call with JSON body: body inserted after params, token appended."""
        params = {
            "appKey": "testkey",
            "shopIdenty": 810094,
            "timestamp": 1710000000,
            "version": "2.0",
        }
        body_json = '{"foo":"bar"}'
        result = build_sign_string(params, body_json=body_json, token_or_secret="shoptoken")
        expected = 'appKeytestkeyshopIdenty810094timestamp1710000000version2.0body{"foo":"bar"}shoptoken'
        assert result == expected

    def test_token_fetch_with_secret(self):
        """Token-fetch: secretKey appended to sign string (not token)."""
        params = {
            "appKey": "mykey",
            "brandId": 999,
            "timestamp": 1700000000,
            "version": "2.0",
        }
        result = build_sign_string(params, body_json=None, token_or_secret="mysecret")
        expected = "appKeymykeybrandId999timestamp1700000000version2.0mysecret"
        assert result == expected

    def test_params_order_is_fixed_not_sorted(self):
        """Param order must be: appKey, shopIdenty, brandId, timestamp, version — not alphabetical."""
        params = {
            "version": "2.0",
            "timestamp": 1710000000,
            "appKey": "testkey",
            "brandId": 32296,
        }
        result = build_sign_string(params, body_json=None, token_or_secret="tok")
        # If alphabetically sorted: appKey, brandId, timestamp, version → same order happens to match
        # but if shopIdenty is present it must come before brandId
        params_with_shop = {
            "version": "2.0",
            "timestamp": 1710000000,
            "appKey": "testkey",
            "shopIdenty": 810094,
        }
        result_shop = build_sign_string(params_with_shop, body_json=None, token_or_secret="tok")
        # shopIdenty before timestamp (fixed order, not sorted order which would put 's' after 'a' 'b')
        assert result_shop == "appKeytestkeyshopIdenty810094timestamp1710000000version2.0tok"

    def test_known_hash(self):
        """Verify SHA-256 hex digest of known input string."""
        known_input = "appKeytestkeybrandId32296timestamp1710000000version2.0mytoken"
        expected_hash = hashlib.sha256(known_input.encode("utf-8")).hexdigest()
        result = compute_sign(
            params={
                "appKey": "testkey",
                "brandId": 32296,
                "timestamp": 1710000000,
                "version": "2.0",
            },
            body_json=None,
            token_or_secret="mytoken",
        )
        assert result == expected_hash
        # Also verify it's a 64-char hex string
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)
