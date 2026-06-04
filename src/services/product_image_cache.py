from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests

from src.models.product import Product

logger = logging.getLogger(__name__)

_MANIFEST_NAME = ".image_manifest.json"


def remote_image_basename(image_url: str) -> str:
    """Имя файла из URL API, например cat_25_956cfef2.jpg."""
    path = urlparse(image_url).path
    name = unquote(path.rsplit("/", 1)[-1]).strip()
    return name or "image.jpg"


def _safe_segment(text: str, *, max_len: int = 120) -> str:
    cleaned = re.sub(r"[^\w.\-]", "_", text.strip())
    return (cleaned or "image")[:max_len]


@dataclass
class ImageCacheStats:
    downloaded: int = 0
    reused: int = 0
    updated: int = 0
    failed: int = 0


class ProductImageCache:
    """Локальное хранение фото каталога: скачивание один раз, обновление при смене имени файла в API."""

    def __init__(self, media_dir: Path) -> None:
        self._media_dir = media_dir
        self._media_dir.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self._media_dir / _MANIFEST_NAME
        self._manifest: dict[str, dict[str, str]] = self._load_manifest()
        self._dirty = False

    def _load_manifest(self) -> dict[str, dict[str, str]]:
        if not self._manifest_path.is_file():
            return {}
        try:
            raw = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Манифест фото: не прочитан %s: %s", self._manifest_path, exc)
            return {}
        if not isinstance(raw, dict):
            return {}
        out: dict[str, dict[str, str]] = {}
        for pid, entry in raw.items():
            if isinstance(entry, dict) and entry.get("remote_name") and entry.get("local_file"):
                out[str(pid)] = {
                    "remote_name": str(entry["remote_name"]),
                    "local_file": str(entry["local_file"]),
                }
        return out

    def _save_manifest(self) -> None:
        tmp = self._manifest_path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(self._manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(self._manifest_path)

    def _local_path_for(self, product_id: str, remote_name: str) -> Path:
        local_name = f"{_safe_segment(product_id)}__{_safe_segment(remote_name)}"
        return self._media_dir / local_name

    def _legacy_path(self, product_id: str) -> Path:
        return self._media_dir / f"{_safe_segment(product_id)}.jpg"

    def _path_if_valid(self, entry: dict[str, str]) -> str:
        path = self._media_dir / entry["local_file"]
        if path.is_file():
            return str(path)
        return ""

    def resolve(self, product: Product) -> str:
        """Локальный путь: из кэша или одноразовая загрузка при новом/изменённом имени файла."""
        if not product.image_url:
            return product.image_local or ""

        remote_name = remote_image_basename(product.image_url)
        pid = product.id
        entry = self._manifest.get(pid)
        target = self._local_path_for(pid, remote_name)

        if entry and entry.get("remote_name") == remote_name:
            cached = self._path_if_valid(entry)
            if cached:
                return cached

        legacy = self._legacy_path(pid)
        if legacy.is_file() and (
            not entry or entry.get("remote_name") == remote_name
        ):
            self._manifest[pid] = {
                "remote_name": remote_name,
                "local_file": legacy.name,
            }
            self._dirty = True
            return str(legacy)

        if entry and entry.get("remote_name") != remote_name:
            old = self._media_dir / entry.get("local_file", "")
            if old.is_file() and old != target:
                try:
                    old.unlink()
                except OSError as exc:
                    logger.warning("Не удалось удалить старое фото %s: %s", old, exc)

        try:
            resp = requests.get(product.image_url, timeout=15)
            resp.raise_for_status()
            target.write_bytes(resp.content)
        except requests.RequestException as exc:
            logger.warning(
                "Не удалось скачать фото %s (%s): %s",
                pid,
                remote_name,
                exc,
            )
            if entry:
                fallback = self._path_if_valid(entry)
                if fallback:
                    return fallback
            if legacy.is_file():
                return str(legacy)
            return ""

        self._manifest[pid] = {
            "remote_name": remote_name,
            "local_file": target.name,
        }
        self._save_manifest()
        return str(target)

    def attach_all(self, products: list[Product]) -> ImageCacheStats:
        stats = ImageCacheStats()
        for product in products:
            if not product.image_url:
                continue

            remote_name = remote_image_basename(product.image_url)
            entry = self._manifest.get(product.id)
            same_name = bool(entry and entry.get("remote_name") == remote_name)
            cached_ok = bool(entry and self._path_if_valid(entry))
            legacy_ok = (
                (not entry or same_name)
                and self._legacy_path(product.id).is_file()
            )
            skip_download = same_name and (cached_ok or legacy_ok)
            was_rename = bool(entry and entry.get("remote_name") != remote_name)

            path = self.resolve(product)
            product.image_local = path

            if not path:
                stats.failed += 1
            elif skip_download:
                stats.reused += 1
            elif was_rename:
                stats.updated += 1
            else:
                stats.downloaded += 1

        self._save_manifest()
        return stats
