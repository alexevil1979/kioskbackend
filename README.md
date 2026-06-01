# Киоск самообслуживания «Ферма»

PyQt6, offline-first каталог, kiosk-режим для Windows 10.

**GitHub:** https://github.com/alexevil1979/kioskbackend  

**Документация:** [`docs/README.md`](docs/README.md) — оглавление, журнал проекта, статус, ТЗ, деплой.

После правок: commit + push (секреты не коммитить — см. [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md)).

## Быстрый старт

```powershell
cd "c:\Users\1\Documents\киоск"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy config\settings.yaml.example config\settings.yaml
python main.py
```

## Оборудование (Т-Банк first)

УМКА и принтер **не обязательны**. Рекомендуется **aQsi 6** от Т-Банка (оплата + чек в одном устройстве).

- [`docs/hardware/00-architecture-tbank-first.md`](docs/hardware/00-architecture-tbank-first.md)
- [`docs/hardware/OPEN_QUESTIONS.md`](docs/hardware/OPEN_QUESTIONS.md)

Два рабочих режима (`hardware.integration_mode`):

| Режим | Описание |
|-------|----------|
| `tbank_aqsi` | aQsi 6 — оплата + чек на терминале |
| `tbank_pos_printer` | PAX + HS-K33 + облачная касса |

Пресеты: [`config/presets/`](config/presets/). Чеклист старта: [`docs/START_CHECKLIST.md`](docs/START_CHECKLIST.md).

### Документы для партнёров

| Документ | Кому |
|----------|------|
| [`docs/CRM_API_SPEC.md`](docs/CRM_API_SPEC.md) | Разработчики CRM |
| [`docs/api/CRM_API_READINESS.md`](docs/api/CRM_API_READINESS.md) | Готовность API для киоска |
| [`docs/TBANK_REQUEST_MODE1.md`](docs/TBANK_REQUEST_MODE1.md) | Т-Банк / Т-Бизнес |
| [`docs/SETUP_NUC_PRINTER_LAN.md`](docs/SETUP_NUC_PRINTER_LAN.md) | Настройка NUC + HS-K33 (режим 2) |

## Структура

| Путь | Назначение |
|------|------------|
| `src/core/` | Конфиг, корзина, навигация, idle, kiosk WinAPI |
| `docs/hardware/` | Оборудование и интеграции |
| `src/models/` | `Product`, `Category` |
| `src/services/` | CRM, каталог, оплата, касса (заглушки) |
| `src/ui/screens/` | Экраны по ТЗ |
| `docs/README.md` | **Оглавление всей документации** |
| `docs/PROJECT_JOURNAL.md` | Журнал создания проекта |
| `docs/STATUS.md` | Текущий статус MVP |
| `docs/PLAN.md` | План и оценки |
| `docs/QUESTIONS.md` | Вопросы для интеграций |

## Kiosk на Windows

- Полноэкранный режим: `app.fullscreen: true` в `config/settings.yaml`
- Блокировка Alt+Tab / Win: hook в `src/core/kiosk_win.py` (Ctrl+Alt+Del — через GPO / Assigned Access)
- Автозапуск: ярлык `main.py` в `shell:startup` или Планировщик заданий

## Текущий MVP

- [x] Все экраны и навигация
- [x] Главное меню, корзина, mock-каталог
- [x] СБП QR (mock оплата через 8 сек)
- [x] Карта (mock 5 сек)
- [x] Бездействие 50/60 сек
- [ ] Реальный CRM / СБП / Т-Банк / УМКА
