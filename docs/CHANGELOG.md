# История изменений

Формат: дата, кратко «что и зачем». Детали — в [PROJECT_JOURNAL.md](PROJECT_JOURNAL.md).

---

## [Unreleased]

- (пусто)

---

## 2026-05-29 — API docs local mirror

- `docs/api/` — локальная копия CRM spec, примеры JSON, CRM_API_READINESS

---

## 2026-05-29 — `45723b4`

**Стабильный старт, демо-фото, счётчик на карточке**

- `image_utils.py` — загрузка изображений при кириллице в пути Windows
- Отложенный старт каталога и fullscreen
- AI демо-ассеты: 12 товаров + `farm_hero.jpg`
- Исправление UI счётчика (− / qty / +) на `ProductCard`
- QSS для `OutlineBtn`, `ProductQty`

---

## 2026-05-29 — `c12e082`

**Portrait UI 1080×1920**

- Вертикальная вёрстка, 2 колонки, `theme_portrait.qss`
- `layout_metrics.py`, скрипт Pillow для заглушек

---

## 2026-05-29 — `32c2c42`

**Initial commit**

- PyQt6 каркас, все экраны, mock CRM и платежи
- Документация hardware, CRM API spec, git workflow
- Конфиг два режима Т-Банк, пресеты aQsi / POS+printer
