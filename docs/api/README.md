# API — локальная документация киоска

Здесь хранятся **локальные копии** контрактов и материалы для интеграции. Оригинал для передачи CRM остаётся в корне `docs/` (см. ниже).

---

## CRM (каталог и заказы)

| Файл | Назначение |
|------|------------|
| [crm/CRM_API_SPEC.md](crm/CRM_API_SPEC.md) | Полная спецификация v1.0 (локальная копия) |
| [CRM_API_READINESS.md](CRM_API_READINESS.md) | **Что есть / чего не хватает** для работы киоска |
| [examples/](examples/) | Примеры JSON запросов и ответов |

Дубликат для заказчика (корень docs): [../CRM_API_SPEC.md](../CRM_API_SPEC.md)

---

## Оплата и чеки (не CRM)

Спецификации внешних API — в `docs/hardware/` (ссылки, не дублируем полностью):

| Интеграция | Документ | Код |
|------------|----------|-----|
| aQsi 6 (режим 1) | [hardware/07-tbank-aqsi.md](../hardware/07-tbank-aqsi.md) | `src/services/tbank_aqsi.py` |
| POS Т-Банк | [hardware/05-tbank-terminal.md](../hardware/05-tbank-terminal.md) | `src/services/payment_card.py` |
| СБП | [hardware/06-tbank-sbp-internet.md](../hardware/06-tbank-sbp-internet.md) | `src/services/payment_sbp.py` |
| Облачная касса | [hardware/08-tbank-pos-printer.md](../hardware/08-tbank-pos-printer.md) | `src/services/fiscal_cloud.py` |
| Принтер HS-K33 | [hardware/04-hs-k33-printer.md](../hardware/04-hs-k33-printer.md) | `src/services/printer_hs_k33.py` |

Запрос в Т-Банк: [../TBANK_REQUEST_MODE1.md](../TBANK_REQUEST_MODE1.md)

---

## Синхронизация копий

При изменении `docs/CRM_API_SPEC.md` обновляйте `docs/api/crm/CRM_API_SPEC.md` (или наоборот — одна версия как master).

После согласования с CRM добавьте:
- `docs/api/crm/openapi.yaml` — если отдадут Swagger;
- `docs/api/examples/` — реальные ответы с test-стенда.
