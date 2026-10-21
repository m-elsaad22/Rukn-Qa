#!/usr/bin/env python3
"""WordPress REST helper for Qatar live applies. Never logs the password."""
from __future__ import annotations

import base64
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE = "https://www.rukn-eltatawer.com/qa"
LOCKED_ID = 2973
UA = "RuknQA-ArticleWave/1.0"


def creds() -> tuple[str, str, str]:
    base = (os.environ.get("WP_BASE_URL") or os.environ.get("WP_BASE") or DEFAULT_BASE).rstrip("/")
    user = (os.environ.get("WP_USERNAME") or os.environ.get("WP_USER") or "").strip()
    password = (os.environ.get("WP_APP_PASSWORD") or "").replace(" ", "").strip()
    if not user or not password:
        raise SystemExit("Set WP_USERNAME and WP_APP_PASSWORD in the environment. Do not commit them.")
    return base, user, password


class WpClient:
    def __init__(self, min_interval: float = 0.25) -> None:
        base, user, password = creds()
        self.base = base
        self.auth = base64.b64encode(f"{user}:{password}".encode()).decode()
        self.min_interval = min_interval
        self._last = 0.0
        self.ctx = ssl.create_default_context()

    def _wait(self) -> None:
        gap = self.min_interval - (time.monotonic() - self._last)
        if gap > 0:
            time.sleep(gap)
        self._last = time.monotonic()

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None, timeout: int = 120) -> tuple[int, Any]:
        url = path if path.startswith("http") else self.base + "/" + path.lstrip("/")
        headers = {
            "Authorization": f"Basic {self.auth}",
            "User-Agent": UA,
            "Accept": "application/json",
        }
        data = None
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        last_err: Exception | None = None
        for attempt in range(5):
            self._wait()
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=timeout, context=self.ctx) as resp:
                    raw = resp.read().decode("utf-8", "replace")
                    body: Any = json.loads(raw) if raw else {}
                    return resp.status, body
            except urllib.error.HTTPError as e:
                raw = e.read().decode("utf-8", "replace")
                try:
                    parsed: Any = json.loads(raw) if raw else {"raw": raw}
                except json.JSONDecodeError:
                    parsed = {"raw": raw[:800]}
                if e.code in {429, 503, 502, 500} and attempt < 4:
                    time.sleep(2 ** attempt)
                    last_err = e
                    continue
                return e.code, parsed
            except Exception as e:  # noqa: BLE001
                last_err = e
                time.sleep(1.5 * (attempt + 1))
        raise SystemExit(f"WP request failed: {method} {path} {last_err}")

    def get(self, path: str) -> tuple[int, Any]:
        return self.request("GET", path)

    def put(self, path: str, payload: dict[str, Any]) -> tuple[int, Any]:
        return self.request("PUT", path, payload)

    def post(self, path: str, payload: dict[str, Any]) -> tuple[int, Any]:
        return self.request("POST", path, payload)
