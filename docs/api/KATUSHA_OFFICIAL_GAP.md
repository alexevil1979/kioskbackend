# Официальный Kiosk API vs киоск PyQt6 — что есть и чего не хватает

**Официальная документация:** [admin.katushamarket.ru/docs/kiosk-api](https://admin.katushamarket.ru/docs/kiosk-api)  
**Локальная копия:** [katusha/KIOSK_API_OFFICIAL.md](katusha/KIOSK_API_OFFICIAL.md)

**Наша старая спецификация** (`CRM_API_SPEC.md`) — **черновик для CRM**, он **не совпадает** с боевым API Катюши.

---

## Главные отличия (критично)

| Тема | Официальный API Катюша | Наш киоск сейчас |
|------|------------------------|------------------|
| **Base URL** | `{origin}/api/external/kiosk` | `CRM_API_BASE_URL` → часто `/api/v1` (неверно) |
| **Авторизация** | `X-Kiosk-Key: ключ` | `Authorization: Bearer` + опционально `X-Kiosk-Id` |
| **Каталог** | один `GET /catalog` | `GET /categories` + `GET /products` (нет в официале) |
| **Товар** | `product_id` + `variant_id`, весовые | один `id`, без вариантов |
| **Заказ** | `POST /order/create` + status + payment-confirm + receipt | **СБП (qr_sbp)** в `payment_sbp.py` + `crm_client`; карта — в работе |
| **Смена** | `session_active` в `/health` | не проверяем |
| **СБП** | QR из ответа `order/create` | mock QR локально |
| **Карта** | `payment-confirm` после терминала | mock / aQsi отдельно |

---

## По разделам документации

### auth — есть в доке, в коде неверно

| В доке | У нас |
|--------|--------|
| `X-Kiosk-Key` | `Bearer` в `HttpCRMClient` — **нужно заменить** |
| Ключ 64 символа из админки | `CRM_API_KEY` / `KIOSK_API_KEY` в `.env` — **ок**, имя переменной обновить |

### base — URL нужно поправить в `.env`

Правильный шаблон:

```env
KIOSK_API_BASE_URL=https://admin.katushamarket.ru/api/external/kiosk
KIOSK_API_KEY=ваш_ключ_из_админки
```

Уточнить у заказчика **боевой origin** (может быть не `admin.`, а отдельный API-хост).

### endpoints — что покрыто

| Эндпоинт | В официале | В киоске |
|----------|------------|----------|
| `GET /health` | да | частично (`is_online`, без разбора `session_active`) |
| `GET /catalog` | да | **нет** (ждём `/categories` + `/products`) |
| `POST /order/create` | да | **нет** |
| `GET /order/{id}/status` | да | **нет** |
| `POST /order/{id}/payment-confirm` | да | **нет** |
| `GET /order/{id}/receipt` | да | **нет** (есть mock печать HS-K33 / aQsi) |

### fields — в каталоге не хватает в модели

Не обрабатываем в `Product` / UI:

- `variant_id`, `variant_name`
- `is_weight_variable`, `price_per_weight_unit`, `min_weight`, `max_weight`
- `available_quantity` vs наш `stock`
- `main_category_id` / `main_category_name` (категории из товара, не отдельный список)
- `images[]`, `producer`
- составной `id` вида `"5_12"`

### flows — не реализованы end-to-end

| Сценарий | Статус |
|----------|--------|
| СБП: catalog → create → QR → poll status → receipt | **нет** (mock) |
| Карта: create → терминал → payment-confirm → receipt | **нет** |
| Блокировка при `session_active: false` | **нет** |

### python — можно взять как эталон

Пример из доки совпадает с целевой архитектурой киоска — перенести в `KatushaKioskClient` (новый клиент).

### errors — частично

| Код | Обработка в киоске |
|-----|-------------------|
| 401 | лог, offline — **добавить сообщение «неверный ключ»** |
| 403 остаток | **нет** (корзина не знает API) |
| 404 | **нет** |
| 400 | **нет** |

---

## Что уже есть в проекте (полезно сохранить)

- Polling каталога (`CatalogStore`)
- Offline-кэш при сбое сети
- UI: меню, корзина, оплата, успех
- Mock для разработки без ключа
- `.env` для секретов (нужно переименовать/дополнить под `KIOSK_*`)
- Интеграция aQsi / POS — **параллельный** путь; официальный API описывает **свой** QR и `payment-confirm` для карты

---

## Рекомендуемый план доработки

1. **Клиент API** — новый `KatushaKioskClient` (или переписать `HttpCRMClient`):
   - заголовок `X-Kiosk-Key`
   - base `/api/external/kiosk`
   - `GET /catalog` → маппинг в `Category` + `Product`
2. **Модели** — `ProductVariant`, весовые поля, `session_active`
3. **Оплата СБП** — `order/create` + poll `status` + `receipt_text`
4. **Оплата карта** — `order/create` (card) + терминал + `payment-confirm`
5. **Конфиг** — `KIOSK_API_BASE_URL`, `KIOSK_API_KEY` в `.env.example`
6. **Документация** — пометить `CRM_API_SPEC.md` как «целевой черновик», источник истины — `KIOSK_API_OFFICIAL.md`

---

## Чего нет даже в официальной доке (уточнить у заказчика)

- Production URL, если не `admin.katushamarket.ru`
- Webhook vs только polling для СБП
- Связь с aQsi: официальный flow — QR/confirm через **этот** API, не через aQsi Cloud
- Нужен ли одновременно CRM_API_SPEC или только Kiosk API

---

## Переменные окружения (актуальные)

```env
KIOSK_API_BASE_URL=https://admin.katushamarket.ru/api/external/kiosk
KIOSK_API_KEY=
CRM_USE_MOCK=false
```

`CRM_API_KEY` — синоним `KIOSK_API_KEY` (обратная совместимость).
