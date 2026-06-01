# Конфигурация (`config/settings.yaml`)

Образец: `config/settings.yaml.example`.  
Локальный файл `config/settings.yaml` **не коммитится** (секреты, IP, ключи).

---

## `app`

| Ключ | Описание | По умолчанию |
|------|----------|--------------|
| `title` | Заголовок окна | «Ферма — киоск» |
| `fullscreen` | Полноэкранный режим | `true` |
| `orientation` | `portrait` / `landscape` | `portrait` |
| `screen_width` / `screen_height` | Размер окна | 1080 × 1920 |

---

## `idle`

| Ключ | Описание |
|------|----------|
| `warning_seconds` | Предупреждение бездействия |
| `reset_seconds` | Полный сброс (корзина + старт) |

---

## `catalog`

| Ключ | Описание |
|------|----------|
| `poll_interval_sec` | Интервал опроса CRM |
| `media_dir` | Кэш фото товаров |

---

## `crm`

| Ключ | Описание |
|------|----------|
| `base_url` | URL API (лучше через `CRM_API_BASE_URL` в `.env`) |
| `api_key` | Bearer (лучше через `CRM_API_KEY` в `.env`) |
| `kiosk_id` | ID точки (`CRM_KIOSK_ID`) |
| `use_mock` | `true` — 12 демо-товаров; `false` — HTTP API |
| `catalog_mode` | `split` — `/categories` + `/products`; `combined` — `/kiosk/catalog` |

Полный список переменных: [api/ENV.md](api/ENV.md).

---

## `payment` / `fiscal`

Заглушки СБП и облачной кассы. Ключи Т-Банка — в `.env` или `settings.yaml` (не в git).

---

## `hardware.integration_mode`

| Значение | Режим |
|----------|--------|
| `tbank_aqsi` | aQsi 6 (основной) |
| `tbank_pos_printer` | POS + HS-K33 + облако |
| `tbank_pos_sbp` | Режим 2 + СБП на экране |
| `legacy_umka` | УМКА + принтер (старое) |

### Подсекции

- `hardware.aqsi` — API aQsi (`use_mock`, `api_key`)
- `hardware.tbank_terminal` — IP/POS Smart Sale
- `hardware.printer` — HS-K33 ESC/POS (`host`, `port`, `enabled`)
- `hardware.network` / `nuc` — IP в LAN

Готовые профили: скопировать из `config/presets/mode_aqsi.yaml` или `mode_pos_printer.yaml`.

---

## `.env`

См. `.env.example` — дублирование чувствительных полей (опционально).

---

## Kiosk

```yaml
kiosk:
  block_keys: true   # Win API hook
```

На dev-машине hook может не установиться — см. лог `src.core.kiosk_win`.
