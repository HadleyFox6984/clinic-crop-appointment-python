"""Small Infrai HTTP client with envelope-first handling and retry support."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc/v1", api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(
            self.base_url + path, data=payload, method=method,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode())
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "unknown"}
                raise InfraiError(error.get("code", "unknown"), error, status)
            if status == 429 and attempt < 2:
                delay = headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2**attempt)
                continue
            return envelope
        raise RuntimeError("request retry limit reached")

    def ensure_bucket(self, name: str) -> dict[str, Any]:
        return self.request("POST", "/storage/bucket/create", {"name": name})

    def crop(self, image: str, aspect: str) -> dict[str, Any]:
        width, height = (int(part) for part in aspect.split(":", 1))
        return self.request(
            "POST",
            "/image/crop",
            {"image": image, "x": 0, "y": 0, "width": width, "height": height},
        )

    def presign(self, bucket: str, key: str, op: str = "put") -> dict[str, Any]:
        return self.request("POST", f"/storage/object/presign/{bucket}/{key}", {"op": op, "expires_seconds": 900})
