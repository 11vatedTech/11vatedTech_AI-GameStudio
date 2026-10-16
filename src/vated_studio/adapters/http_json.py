from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from typing import Any
import json

from ..errors import StudioError


def request_json(base_url: str, path: str, *, method: str = "GET", payload: Any = None,
                 query: dict[str, Any] | None = None, timeout: float = 30.0, max_bytes: int = 32_000_000) -> Any:
    url = base_url.rstrip("/") + "/" + path.lstrip("/")
    if query:
        url += "?" + urlencode({k: v for k, v in query.items() if v is not None}, doseq=True)
    data = None if payload is None else json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise StudioError("Provider response exceeded configured size limit", code="response_too_large", details={"url": url})
            content_type = response.headers.get("Content-Type", "")
            if "json" not in content_type.lower() and raw:
                raise StudioError("Provider did not return JSON", code="unexpected_content_type", details={"url": url, "content_type": content_type})
            return json.loads(raw.decode("utf-8")) if raw else {}
    except HTTPError as exc:
        body = exc.read(4096).decode("utf-8", errors="replace")
        raise StudioError("Provider HTTP request failed", code="provider_http_error", details={"url": url, "status": exc.code, "body": body}, http_status=502) from exc
    except URLError as exc:
        raise StudioError("Provider is unavailable", code="provider_unavailable", details={"url": url, "reason": str(exc.reason)}, http_status=503) from exc
    except (TimeoutError, json.JSONDecodeError) as exc:
        raise StudioError("Provider request timed out or returned invalid JSON", code="provider_protocol_error", details={"url": url, "reason": str(exc)}, http_status=502) from exc


def request_bytes(base_url: str, path: str, *, query: dict[str, Any] | None = None, timeout: float = 30.0, max_bytes: int = 64_000_000) -> bytes:
    url = base_url.rstrip("/") + "/" + path.lstrip("/")
    if query:
        url += "?" + urlencode({k: v for k, v in query.items() if v is not None}, doseq=True)
    try:
        with urlopen(Request(url, headers={"Accept": "image/*,application/octet-stream"}), timeout=timeout) as response:
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise StudioError("Provider image exceeded configured size limit", code="response_too_large", details={"url": url})
            return raw
    except (HTTPError, URLError, TimeoutError) as exc:
        raise StudioError("Provider binary request failed", code="provider_binary_error", details={"url": url, "reason": str(exc)}, http_status=502) from exc
