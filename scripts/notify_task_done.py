#!/usr/bin/env python3
"""Отправка уведомления в Telegram о завершении задачи."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path, override=True)
    except ImportError:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def _send(text: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise SystemExit(
            "Задайте TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID в .env (см. .env.example)"
        )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if not body.get("ok"):
        raise SystemExit(f"Telegram API error: {body}")


def main() -> None:
    _load_env()
    detail = " ".join(sys.argv[1:]).strip()
    text = "Закончил выполнение задачи"
    if detail:
        text = f"{text}: {detail}"
    _send(text)
    print("Telegram: сообщение отправлено")


if __name__ == "__main__":
    main()
