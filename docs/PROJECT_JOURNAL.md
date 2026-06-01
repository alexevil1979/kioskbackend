# Журнал создания проекта

Хронология работ над киоском «Ферма». Новые записи добавляются **сверху** (последнее — первым).

---

## 2026-05-29 — Локальная копия API CRM и анализ пробелов

| Что сделано | Детали |
|-------------|--------|
| `docs/api/` | Копия CRM_API_SPEC, примеры JSON, CRM_API_READINESS |
| Анализ | Матрица: спецификация vs код vs блокеры CRM vs оплата |

---

## 2026-05-29 — Демо-фото, стабильность UI, документация

| Что сделано | Детали |
|-------------|--------|
| AI-демо ассеты | `assets/demo_products/1–12.jpg`, `assets/branding/farm_hero.jpg` — единый стиль каталога |
| Загрузка картинок | `src/ui/image_utils.py` — `QImage.fromData(bytes)` для путей с кириллицей (Windows) |
| Старт приложения | Отложенные `catalog.refresh()` и fullscreen в `main_window.py` |
| Счётчик на карточке | Скрытие блока −/qty/+ при qty=0; QSS `OutlineBtn`, `ProductQty` |
| Git | Коммит `45723b4`, push `main` |
| Документация | Структура `docs/`, этот журнал, STATUS, DEVELOPMENT и др. |

---

## 2026-05-29 — Портретный UI 1080×1920

| Что сделано | Детали |
|-------------|--------|
| Ориентация | `app.orientation: portrait`, 1080×1920, 2 колонки товаров |
| Стили | `theme_portrait.qss`, `layout_metrics.py` |
| Демо-картинки (Pillow) | `scripts/generate_product_images.py`, первые заглушки в `assets/` |
| Git | Коммит `c12e082` |

---

## 2026-05-29 — Initial commit (MVP каркас)

| Что сделано | Детали |
|-------------|--------|
| Каркас | `main.py`, `src/app.py`, `requirements.txt`, `config/settings.yaml.example` |
| Core | config, cart, state_machine, idle_timer, kiosk_win (блок клавиш) |
| UI | Все экраны: старт, меню, корзина, оплата СБП/карта, успех, ошибка, офлайн, idle overlay |
| Сервисы | mock CRM, catalog_sync, заглушки SBP, card, aQsi, cloud fiscal, printer, УМКА |
| Документы | PLAN, ARCHITECTURE, CRM_API_SPEC, hardware/*, GIT_WORKFLOW, START_CHECKLIST |
| Git | Коммит `32c2c42`, репозиторий kioskbackend |

---

## 2026-05-29 — Проектирование (до кода)

| Что сделано | Детали |
|-------------|--------|
| ТЗ | Экраны, UX, offline-first, PyQt6 по сообщению заказчика |
| Железо | `киоск параметры.txt`: NUC, 32″, HS-K33, УМКА, Т-Банк |
| Стратегия оплаты | **Т-Банк first**; УМКА не обязательна |
| Два режима | `tbank_aqsi` (aQsi 6) и `tbank_pos_printer` (PAX + принтер + облако) |
| Пресеты | `config/presets/mode_aqsi.yaml`, `mode_pos_printer.yaml` |
| Документы для партнёров | CRM_API_SPEC, TBANK_REQUEST_MODE1, SETUP_NUC_PRINTER_LAN |

---

## Шаблон новой записи

```markdown
## ГГГГ-ММ-ДД — Краткий заголовок

| Что сделано | Детали |
|-------------|--------|
| ... | ... |
```
