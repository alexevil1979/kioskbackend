# Переменные окружения (.env)

Секреты и URL API **не хранятся в git**. Задаются в файле `.env` в корне проекта (скопируйте из [`.env.example`](../../.env.example)).

При старте `load_settings()`:

1. Читает `config/settings.yaml`
2. Загружает `.env` (пакет `python-dotenv`)
3. Переменные окружения **перекрывают** YAML

---

## CRM (каталог)

| Переменная | Куда попадает | Описание |
|------------|---------------|----------|
| `CRM_API_BASE_URL` | `crm.base_url` | Базовый URL API, напр. `https://katushamarket.ru/api/v1` |
| `CRM_BASE_URL` | то же | Синоним |
| `CRM_API_KEY` | `crm.api_key` | Bearer token |
| `CRM_KIOSK_ID` | `crm.kiosk_id` | ID точки киоска |
| `CRM_USE_MOCK` | `crm.use_mock` | `true` / `false` |
| `CRM_CATALOG_MODE` | `crm.catalog_mode` | `split` или `combined` |

### Авто-режим

Если заданы **`CRM_API_KEY`** и **`CRM_API_BASE_URL`**, а `CRM_USE_MOCK` не указан — киоск переключается на **HTTP API** (`use_mock: false`).

### Пример `.env` для боя

```env
CRM_API_BASE_URL=https://katushamarket.ru/api/v1
CRM_API_KEY=ваш_ключ_из_ЛК
CRM_KIOSK_ID=kiosk-farm-01
CRM_USE_MOCK=false
```

Проверка (без UI):

```powershell
.\.venv\Scripts\pip install python-dotenv
.\.venv\Scripts\python -c "from src.core.config import load_settings; s=load_settings(); print(s.crm)"
```

---

## Прочие интеграции

| Переменная | Назначение |
|------------|------------|
| `AQSI_API_KEY` | `hardware.aqsi.api_key` |
| `AQSI_API_BASE` | `hardware.aqsi.api_base` |
| `TBANK_TERMINAL_KEY` | СБП |
| `TBANK_TERMINAL_PASSWORD` | СБП |
| `FISCAL_CLOUD_PUBLIC_ID` | Облачная касса |
| `FISCAL_CLOUD_API_SECRET` | Облачная касса |

---

## Связь с mini app

Telegram-магазин: [699.ru](https://699.ru/) · сайт: [katushamarket.ru](https://katushamarket.ru)

URL API в спецификации: [crm/CRM_API_SPEC.md](crm/CRM_API_SPEC.md) §1, §9.  
Точный path (`/api/v1`, `/v1`) — уточнить у backend-команды, если health отвечает 404.
