# Документация проекта «Ферма» (киоск самообслуживания)

**Репозиторий:** https://github.com/alexevil1979/kioskbackend  
**Стек:** Python 3.11+, PyQt6, Windows 10, offline-first каталог.

Документацию ведём **по ходу разработки**: после заметных изменений обновляйте [PROJECT_JOURNAL.md](PROJECT_JOURNAL.md), [STATUS.md](STATUS.md) и при релизах — [CHANGELOG.md](CHANGELOG.md).

---

## Быстрая навигация

| Раздел | Файл | Для кого |
|--------|------|----------|
| **Журнал создания** | [PROJECT_JOURNAL.md](PROJECT_JOURNAL.md) | Вся команда — что сделано и когда |
| **Текущий статус** | [STATUS.md](STATUS.md) | Заказчик, PM |
| **Требования** | [REQUIREMENTS.md](REQUIREMENTS.md) | ТЗ, приёмка |
| **План и оценки** | [PLAN.md](PLAN.md) | Планирование |
| **Разработка** | [DEVELOPMENT.md](DEVELOPMENT.md) | Разработчики |
| **Конфигурация** | [CONFIGURATION.md](CONFIGURATION.md) | DevOps, интеграторы |
| **UI и экраны** | [UI_AND_SCREENS.md](UI_AND_SCREENS.md) | UI/UX, тестирование |
| **Архитектура** | [ARCHITECTURE.md](ARCHITECTURE.md) | Разработчики |
| **Ассеты** | [ASSETS.md](ASSETS.md) | Контент, дизайн |
| **Деплой** | [DEPLOYMENT.md](DEPLOYMENT.md) | NUC, поле |
| **Установка Win10** | [INSTALL_TERMINAL_WIN10.md](INSTALL_TERMINAL_WIN10.md) | Терминал, монтаж |
| **История версий** | [CHANGELOG.md](CHANGELOG.md) | Все |
| **Git** | [GIT_WORKFLOW.md](GIT_WORKFLOW.md) | Разработчики |
| **Вопросы заказчику** | [QUESTIONS.md](QUESTIONS.md) | Менеджер |
| **Чеклист старта** | [START_CHECKLIST.md](START_CHECKLIST.md) | Запуск проекта |

---

## API (локальная копия)

| Документ | Назначение |
|----------|------------|
| [**api/README.md**](api/README.md) | Оглавление API-документации |
| [**api/CRM_API_READINESS.md**](api/CRM_API_READINESS.md) | **Что есть / чего не хватает** для киоска |
| [**design/KATUSHA_UI.md**](design/KATUSHA_UI.md) | Вёрстка mini app 699.ru → киоск |
| [api/crm/CRM_API_SPEC.md](api/crm/CRM_API_SPEC.md) | Спецификация CRM (копия) |
| [api/examples/](api/examples/) | Примеры JSON |

## Интеграции и партнёры

| Документ | Назначение |
|----------|------------|
| [CRM_API_SPEC.md](CRM_API_SPEC.md) | ТЗ API для передачи разработчикам CRM |
| [TBANK_REQUEST_MODE1.md](TBANK_REQUEST_MODE1.md) | Запрос в Т-Банк (режим aQsi) |
| [SETUP_NUC_PRINTER_LAN.md](SETUP_NUC_PRINTER_LAN.md) | NUC + принтер HS-K33 (режим 2) |

---

## Оборудование (`docs/hardware/`)

| Документ | Тема |
|----------|------|
| [hardware/README.md](hardware/README.md) | Оглавление железа |
| [hardware/00-architecture-tbank-first.md](hardware/00-architecture-tbank-first.md) | Стратегия Т-Банк first |
| [hardware/00-network-topology.md](hardware/00-network-topology.md) | Сеть, switch |
| [hardware/01-payment-and-receipt-flow.md](hardware/01-payment-and-receipt-flow.md) | Поток оплаты и чека |
| [hardware/07-tbank-aqsi.md](hardware/07-tbank-aqsi.md) | aQsi 6 (режим 1) |
| [hardware/08-tbank-pos-printer.md](hardware/08-tbank-pos-printer.md) | POS + принтер (режим 2) |
| [hardware/OPEN_QUESTIONS.md](hardware/OPEN_QUESTIONS.md) | Открытые вопросы |

Полный список файлов — в [hardware/README.md](hardware/README.md).

---

## Исходные материалы заказчика

- `киоск параметры.txt` (корень репозитория) — железо, сеть, режимы.
- Сообщения в переписке / ТЗ на экраны и UX — сводка в [REQUIREMENTS.md](REQUIREMENTS.md).

---

## Как поддерживать документацию

1. Закончили задачу → строка в [PROJECT_JOURNAL.md](PROJECT_JOURNAL.md) (дата, что сделано, файлы).
2. Изменился MVP / интеграции → [STATUS.md](STATUS.md).
3. Push в `main` → при необходимости запись в [CHANGELOG.md](CHANGELOG.md).
4. Новый экран или параметр config → [UI_AND_SCREENS.md](UI_AND_SCREENS.md) / [CONFIGURATION.md](CONFIGURATION.md).

Правило Cursor: `.cursor/rules/git-push-after-changes.mdc` — commit + push после правок кода (без секретов).
