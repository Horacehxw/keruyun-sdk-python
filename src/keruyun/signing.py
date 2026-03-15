"""
Keruyun v2.0 API signing algorithm.

Sign string format:
  k1v1k2v2...body{json}token_or_secret

Where param keys appear in FIXED order (not alphabetical):
  appKey, shopIdenty, brandId, timestamp, token, version

Only params present in the call are included.
Token (or secretKey for token-fetch) is ALSO appended after body (no key prefix).

Note: For authenticated calls the token appears both as a named param in the
sign string (between timestamp and version) AND appended at the end.
For token-fetch calls only secretKey is appended (no token param present).
"""

import hashlib

# Fixed order for signing — only keys present in params are included.
# 'token' sits between 'timestamp' and 'version' in lexicographic order.
_SIGN_PARAM_ORDER = ["appKey", "shopIdenty", "brandId", "timestamp", "token", "version"]


def build_sign_string(
    params: dict,
    body_json: str | None,
    token_or_secret: str,
) -> str:
    """
    Concatenate params in fixed order, optionally append body, then append token/secret.

    Args:
        params: Query parameters dict (values will be converted to str).
        body_json: Compact JSON string of request body, or None for GET requests.
        token_or_secret: The access token (authenticated calls) or secretKey (token-fetch).

    Returns:
        Raw sign string before hashing.
    """
    parts = []
    for key in _SIGN_PARAM_ORDER:
        if key in params:
            parts.append(f"{key}{params[key]}")

    if body_json:
        parts.append(f"body{body_json}")

    parts.append(token_or_secret)

    return "".join(parts)


def compute_sign(
    params: dict,
    body_json: str | None,
    token_or_secret: str,
) -> str:
    """
    Compute SHA-256 hex digest of the sign string.

    Args:
        params: Query parameters dict.
        body_json: Compact JSON string of request body, or None.
        token_or_secret: The access token or secretKey.

    Returns:
        Lowercase SHA-256 hex digest string (64 characters).
    """
    sign_str = build_sign_string(params, body_json, token_or_secret)
    return hashlib.sha256(sign_str.encode("utf-8")).hexdigest()
