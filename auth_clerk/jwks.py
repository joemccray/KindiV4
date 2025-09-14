from __future__ import annotations

from typing import Any

import httpx
from cachetools import TTLCache

_JWKS_CACHE = TTLCache(maxsize=2, ttl=60 * 10)  # 10 minutes


class JWKSClient:
    def __init__(self, jwks_url: str):
        self.jwks_url = jwks_url

    def fetch_jwks(self) -> dict[str, Any]:
        if cached := _JWKS_CACHE.get(self.jwks_url):
            return cached
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(self.jwks_url)
            resp.raise_for_status()
            data = resp.json()
        _JWKS_CACHE[self.jwks_url] = data
        return data

    def get_key(self, kid: str) -> dict[str, Any] | None:
        jwks = self.fetch_jwks()
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        # Kid not found: clear cache and retry once (handles rotation)
        _JWKS_CACHE.pop(self.jwks_url, None)
        jwks = self.fetch_jwks()
        return next(
            (key for key in jwks.get("keys", []) if key.get("kid") == kid), None
        )
