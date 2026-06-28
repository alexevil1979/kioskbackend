from __future__ import annotations

import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_LOCK = threading.Lock()
_SEPARATOR = "=" * 80


def _is_order_api_path(path: str) -> bool:
    norm = path.strip("/")
    return norm == "order/create" or norm.startswith("order/")


def _is_qr_sbp_create(path: str, body: dict[str, Any] | None) -> bool:
    norm = path.strip("/")
    if norm != "order/create" or not body:
        return False
    return str(body.get("payment_method") or "").lower() in ("qr_sbp", "sbp", "qr")


def _sanitize_value(key: str, value: Any) -> Any:
    if key in ("qr_code_image", "qrCodeImage") and isinstance(value, str) and len(value) > 120:
        preview = value[:80].replace("\n", "")
        return (
            f"<base64 image, {len(value)} chars, preview: {preview}…>"
        )
    if isinstance(value, dict):
        return {k: _sanitize_value(k, v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_value("", item) for item in value]
    return value


def _format_json(data: Any) -> str:
    if isinstance(data, str):
        text = data.strip()
        if not text:
            return "(empty)"
        try:
            parsed = json.loads(text)
            return json.dumps(
                _sanitize_value("", parsed),
                ensure_ascii=False,
                indent=2,
            )
        except ValueError:
            if len(text) > 8000:
                return text[:8000] + f"\n… [text truncated, total {len(text)} chars]"
            return text
    return json.dumps(
        _sanitize_value("", data),
        ensure_ascii=False,
        indent=2,
    )


class PaymentQrApiTrace:
    """Отдельный файл: сырые тела запросов/ответов API оплаты СБП (QR)."""

    def __init__(self, *, enabled: bool, file_path: Path) -> None:
        self._enabled = enabled
        self._path = file_path
        if enabled:
            self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    def should_trace_post(self, path: str, body: dict[str, Any] | None) -> bool:
        if not self._enabled:
            return False
        norm = path.strip("/")
        if norm.startswith("order/") and norm.endswith("/cancel"):
            return True
        return _is_qr_sbp_create(path, body)

    def should_trace_get(self, path: str) -> bool:
        if not self._enabled:
            return False
        return _is_order_api_path(path) and path.strip("/") != "order/create"

    def log_request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> None:
        lines = [
            _SEPARATOR,
            self._ts_header(method, "REQUEST"),
            f"URL: {url}",
        ]
        if params:
            lines.append(f"Query: {json.dumps(params, ensure_ascii=False)}")
        if body is not None:
            lines.append("Body:")
            lines.append(_format_json(body))
        self._append(lines)

    def log_response(
        self,
        method: str,
        url: str,
        status_code: int,
        raw_body: str,
    ) -> None:
        lines = [
            "-" * 80,
            self._ts_header(method, f"RESPONSE | HTTP {status_code}"),
            f"URL: {url}",
            "Body (raw):",
            _format_json(raw_body),
            _SEPARATOR,
            "",
        ]
        self._append(lines)

    def log_error(
        self,
        method: str,
        url: str,
        error: str,
        *,
        status_code: int | None = None,
        raw_body: str | None = None,
    ) -> None:
        status = f" | HTTP {status_code}" if status_code else ""
        lines = [
            "-" * 80,
            self._ts_header(method, f"ERROR{status}"),
            f"URL: {url}",
            f"Error: {error}",
        ]
        if raw_body:
            lines.append("Body (raw):")
            lines.append(_format_json(raw_body))
        lines.extend([_SEPARATOR, ""])
        self._append(lines)

    def _ts_header(self, method: str, kind: str) -> str:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return f"{ts} | {method} | {kind}"

    def _append(self, lines: list[str]) -> None:
        block = "\n".join(lines) + "\n"
        try:
            with _LOCK:
                with self._path.open("a", encoding="utf-8") as f:
                    f.write(block)
        except OSError as exc:
            logger.warning("Не удалось записать payment QR API trace: %s", exc)
