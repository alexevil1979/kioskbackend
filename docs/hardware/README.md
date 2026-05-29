# Оборудование киоска «Ферма»

**Базовая стратегия: Т-Банк first** — УМКА и HS-K33 **не обязательны**.

| Документ | Содержание |
|----------|------------|
| [**00-architecture-tbank-first.md**](00-architecture-tbank-first.md) | **Главный документ:** aQsi 6 vs PAX vs СБП |
| [00-network-topology.md](00-network-topology.md) | Схема LAN/Wi‑Fi (упрощённая) |
| [01-payment-and-receipt-flow.md](01-payment-and-receipt-flow.md) | Бизнес-процесс оплаты и чека |
| [02-nuc-kiosk-pc.md](02-nuc-kiosk-pc.md) | NUC i3, Windows 10 Pro |
| [07-tbank-aqsi.md](07-tbank-aqsi.md) | **aQsi 6** — всё в одном |
| [**08-tbank-pos-printer.md**](08-tbank-pos-printer.md) | **POS + принтер, без УМКА** |
| [05-tbank-terminal.md](05-tbank-terminal.md) | PAX + Smart Sale |
| [03-umka-01-fa.md](03-umka-01-fa.md) | УМКА — *опционально* (`legacy_umka`) |
| [04-hs-k33-printer.md](04-hs-k33-printer.md) | HS-K33 — *опционально* |
| [06-tbank-sbp-internet.md](06-tbank-sbp-internet.md) | СБП через интернет (NUC → роутер) |
| [SOURCES.md](SOURCES.md) | Все ссылки |
| [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) | Что ещё нужно от вас |

**Код:** настройки `hardware.*` в `config/settings.yaml`, сервисы `fiscal_umka.py`, `payment_card.py`, `printer_hs_k33.py`.
