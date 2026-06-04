# Kiosk API v1.0 — официальная документация (локальная копия)

**Источник:** [admin.katushamarket.ru/docs/kiosk-api](https://admin.katushamarket.ru/docs/kiosk-api)  
**Версия:** v1.0  
**Сайт:** [katushamarket.ru](https://katushamarket.ru) · mini app [699.ru](https://699.ru/)

> Страница в админке — SPA; текст восстановлен из официального бандла `KioskApiDocsView` (май 2026).

---

## auth — Авторизация

Каждый запрос передаёт API-ключ киоска:

```http
X-Kiosk-Key: ваш_api_ключ_64_символа
```

Ключ выдаётся в админке «Катюша» для конкретной станции/киоска.

**Не** `Authorization: Bearer` — только заголовок **`X-Kiosk-Key`**.

---

## base — Базовый URL

```
{origin}/api/external/kiosk
```

Пример (из документации, origin = хост админки):

```
https://admin.katushamarket.ru/api/external/kiosk
```

- Только **HTTPS**
- Тело запросов/ответов: **JSON (UTF-8)**

---

## endpoints — Эндпоинты

### `GET /health`

Проверка API и активности смены на точке.

**Ответ 200 (пример):**

```json
{
  "ok": true,
  "kiosk_id": 1,
  "kiosk_name": "Киоск-1",
  "station_id": 3,
  "session_active": true
}
```

Если `session_active: false` — заказы создавать нельзя (смена не открыта).

---

### `GET /catalog`

Полный каталог точки: товары с остатком > 0, вложенность категорий в полях товара.

**Ответ 200 (фрагмент):**

```json
{
  "session_active": true,
  "total": 5,
  "products": [
    {
      "id": "5_12",
      "product_id": 5,
      "variant_id": 12,
      "name": "Клубника",
      "variant_name": "500г",
      "description": "Свежая ягода",
      "price": 350,
      "unit": "шт",
      "available_quantity": 20,
      "max_quantity_per_order": 5,
      "is_available": true,
      "is_weight_variable": false,
      "image": "https://...",
      "images": [{ "id": 1, "url": "https://...", "is_primary": true }],
      "producer": { "id": 1, "name": "...", "logo_url": "...", "is_verified": true }
    }
  ]
}
```

**Весовой товар** (`is_weight_variable: true`): цена в **`price_per_weight_unit`** (за 100 г), не в `price`.

---

### `POST /order/create`

Создание заказа. Для СБП возвращает QR; для карты — ожидание подтверждения на терминале.

**Тело запроса (пример):**

```json
{
  "items": [
    { "product_id": 5, "variant_id": 12, "quantity": 2 }
  ],
  "payment_method": "qr_sbp",
  "kiosk_order_id": "ваш_идемпотентный_id"
}
```

| Поле | Значения |
|------|----------|
| `payment_method` | `"qr_sbp"` или `"card"` |
| `kiosk_order_id` | Опционально, идемпотентность на стороне киоска |

**Ответ 200 (СБП, пример):**

```json
{
  "order_id": 1234,
  "total_amount": 700,
  "payment_method": "qr_sbp",
  "payment_id": "pay_abc123",
  "qr_code_payload": "https://qr.nspk.ru/...",
  "qr_code_image": "data:image/png;base64,...",
  "payment_url": null,
  "expires_in_seconds": 300
}
```

---

### `GET /order/{order_id}/status`

Опрос статуса оплаты (рекомендуется **каждые 2 сек**).

**Ответ 200 (пример):**

```json
{
  "order_id": 1234,
  "status": "APPROVED",
  "payment_status": "CONFIRMED",
  "paid": true,
  "cancelled": false,
  "total_amount": 700
}
```

---

### `POST /order/{order_id}/payment-confirm`

Подтверждение оплаты **картой** после успеха на терминале Т-Банк.

**Тело (пример):**

```json
{
  "success": true
}
```

**Ответ при успехе:**

```json
{ "ok": true, "order_id": 1234, "status": "APPROVED", "paid": true }
```

При `success: false` — отмена заказа.

---

### `GET /order/{order_id}/receipt`

Текст чека после оплаты.

**Ответ 200 (фрагмент):**

```json
{
  "order_id": 1234,
  "station_name": "Киоск-1",
  "paid_at": "29.05.2026 14:30",
  "total_amount": 700,
  "items": [{ "name": "Клубника 500г", "quantity": 2, "price": 350, "total": 700 }],
  "receipt_text": "================================\n..."
}
```

`receipt_text` — для печати ESC/POS или показа на экране.

---

## fields — Поля (кратко)

### Идентификация товара

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Составной `"product_id_variant_id"` |
| `product_id` | int | ID товара |
| `variant_id` | int | ID варианта (фасовка) |
| `main_category_id` | int | ID главной категории |
| `main_category_name` | string | Название категории для UI |

### Отображение

| Поле | Тип | Описание |
|------|-----|----------|
| `name`, `variant_name`, `description` | string | Названия |
| `image`, `images[]` | string / array | Фото |

### Цена и остатки

| Поле | Тип | Описание |
|------|-----|----------|
| `price` | float | Цена за единицу (не весовой) |
| `price_per_weight_unit` | float\|null | Цена за 100 г (весовой) |
| `unit` | string\|null | кг, шт, … |
| `available_quantity` | int | Остаток |
| `max_quantity_per_order` | int\|null | Лимит в заказе |
| `is_weight_variable` | bool | Весовой товар |
| `min_weight`, `max_weight` | float\|null | Для весовых |

### Позиция заказа

| Поле | Тип | Обяз. |
|------|-----|-------|
| `product_id` | int | да |
| `variant_id` | int | да |
| `quantity` | number | да (для весовых — вес в граммах) |

---

## flows — Сценарии

### СБП (QR на экране)

1. `GET /health` → `session_active: true`
2. `GET /catalog`
3. `POST /order/create` (`payment_method: "qr_sbp"`)
4. Показать `qr_code_payload` / `qr_code_image`
5. `GET /order/{id}/status` каждые 2 с → `paid: true`
6. `GET /order/{id}/receipt` → печать/успех

### Карта (терминал)

1. `GET /health`
2. `GET /catalog`
3. `POST /order/create` (`payment_method: "card"`)
4. Оплата на терминале (SDK Т-Банк)
5. `POST /order/{id}/payment-confirm` (`success: true/false`)
6. `GET /order/{id}/receipt`

---

## python — Пример (httpx)

```python
import httpx, time

BASE = "https://admin.katushamarket.ru/api/external/kiosk"
H = {"X-Kiosk-Key": "ваш_ключ"}

health = httpx.get(f"{BASE}/health", headers=H).json()
if not health.get("session_active"):
    raise SystemExit("Смена не активна")

products = httpx.get(f"{BASE}/catalog", headers=H).json()["products"]
p = products[0]

order = httpx.post(f"{BASE}/order/create", headers=H, json={
    "items": [{"product_id": p["product_id"], "variant_id": p["variant_id"], "quantity": 1}],
    "payment_method": "qr_sbp",
}).json()

while True:
    s = httpx.get(f"{BASE}/order/{order['order_id']}/status", headers=H).json()
    if s.get("paid"):
        receipt = httpx.get(f"{BASE}/order/{order['order_id']}/receipt", headers=H).json()
        break
    time.sleep(2)
```

---

## errors — Коды ошибок

| HTTP | Описание |
|------|----------|
| 200 | Успех |
| 401 | Неверный `X-Kiosk-Key` |
| 400 | Нет позиций / неверные items |
| 403 | Недостаточно остатка |
| 404 | Точка или заказ не найден |
| 500 | Ошибка сервера |

---

## Якоря в оригинале

- [#auth](https://admin.katushamarket.ru/docs/kiosk-api#auth)
- [#base](https://admin.katushamarket.ru/docs/kiosk-api#base)
- [#endpoints](https://admin.katushamarket.ru/docs/kiosk-api#endpoints)
- [#fields](https://admin.katushamarket.ru/docs/kiosk-api#fields)
- [#flows](https://admin.katushamarket.ru/docs/kiosk-api#flows)
- [#python](https://admin.katushamarket.ru/docs/kiosk-api#python)
- [#errors](https://admin.katushamarket.ru/docs/kiosk-api#errors)
