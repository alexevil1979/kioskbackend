# Спецификация API CRM для киоска самообслуживания «Ферма»

> **Локальная копия и анализ:** [api/crm/CRM_API_SPEC.md](api/crm/CRM_API_SPEC.md) · [api/CRM_API_READINESS.md](api/CRM_API_READINESS.md)

**Версия:** 1.0  
**Дата:** 2026-05-29  
**Заказчик:** киоск на ферме (NUC, PyQt6, offline-first)  
**Основной режим оплаты:** Т-Банк aQsi 6 (`tbank_aqsi`)  
**Аудитория:** разработчики backend CRM  

Документ описыет **минимальный и рекомендуемый** контракт HTTP API для интеграции с приложением киоска.

---

## 1. Общие требования

| Параметр | Требование |
|----------|------------|
| Протокол | **HTTPS** (TLS 1.2+) в production |
| Формат | **JSON**, кодировка UTF-8 |
| Базовый URL | Передаётся в конфиг киоска: `https://api.example.com/v1` |
| Авторизация | **Bearer token** в заголовке `Authorization: Bearer <api_key>` |
| Идентификация точки | Параметр `kiosk_id` или `store_id` (query/header) — см. §2 |
| Таймаут ответа | ≤ **10 сек** (киоск: `crm.timeout_sec`) |
| Polling каталога | Киоск опрашивает каждые **15–30 сек** |
| Часовой пояс | Все даты в **ISO 8601** с offset, например `2026-05-29T14:30:00+03:00` |

### 1.1. Заголовки запросов от киоска

```http
GET /api/v1/products HTTP/1.1
Host: api.farm.example
Authorization: Bearer <KIOSK_API_KEY>
Accept: application/json
User-Agent: KioskFarm/1.0
X-Kiosk-Id: kiosk-001
```

### 1.2. Коды ответов

| HTTP | Значение для киоска |
|------|---------------------|
| 200 | Успех |
| 401 | Неверный ключ — показать «сервис недоступен», лог |
| 404 | Эндпоинт не найден |
| 429 | Rate limit — повторить позже |
| 5xx | Сервер недоступен — работа на **кэше**, экран офлайн при длительном сбое |

### 1.3. Health check (обязательно)

```http
GET /health
```

**Ответ 200:**
```json
{
  "status": "ok",
  "server_time": "2026-05-29T14:30:00+03:00"
}
```

Киоск использует этот метод для `is_online()` перед обновлением каталога.

---

## 2. Идентификация киоска

В каждом запросе (рекомендуется) передавать идентификатор точки продаж:

| Способ | Пример |
|--------|--------|
| Заголовок | `X-Kiosk-Id: kiosk-farm-01` |
| Query | `?kiosk_id=kiosk-farm-01` |

CRM должна отдавать **цены и остатки**, актуальные для этой точки (склад/магазин/киоск).

---

## 3. Категории товаров

### `GET /categories`

Список категорий для верхней панели киоска.

**Query (опционально):**
- `kiosk_id` — идентификатор киоска

**Ответ 200:**
```json
{
  "categories": [
    {
      "id": "berry",
      "name": "Ягода",
      "sort_order": 1,
      "is_active": true
    },
    {
      "id": "dairy",
      "name": "Молочка",
      "sort_order": 2,
      "is_active": true
    }
  ],
  "updated_at": "2026-05-29T14:00:00+03:00"
}
```

| Поле | Тип | Обяз. | Описание |
|------|-----|-------|----------|
| `id` | string | да | Стабильный ID (латиница/цифры), не менять после публикации |
| `name` | string | да | Название на русском для UI |
| `sort_order` | integer | да | Сортировка слева направо (меньше = левее) |
| `is_active` | boolean | нет | `false` — скрыть на киоске (default: true) |

---

## 4. Товары (каталог)

### `GET /products`

Полный список товаров, доступных на киоске.

**Query (опционально):**
- `kiosk_id`
- `category_id` — фильтр (киоск может запрашивать всё сразу)
- `updated_since` — ISO datetime, только изменённые (для оптимизации)

**Ответ 200:**
```json
{
  "products": [
    {
      "id": "prod-1001",
      "category_id": "berry",
      "name": "Клубника",
      "description": "Свежая, с грядки",
      "price": 450.00,
      "currency": "RUB",
      "stock": 12,
      "unit": "кг",
      "image_url": "https://cdn.farm.example/products/1001.jpg",
      "is_active": true,
      "vat_code": "vat20",
      "updated_at": "2026-05-29T13:55:00+03:00"
    },
    {
      "id": "prod-1002",
      "category_id": "berry",
      "name": "Черника",
      "price": 680.00,
      "currency": "RUB",
      "stock": 0,
      "unit": "кг",
      "image_url": "https://cdn.farm.example/products/1002.jpg",
      "is_active": true
    }
  ],
  "updated_at": "2026-05-29T14:00:00+03:00"
}
```

| Поле | Тип | Обяз. | Описание |
|------|-----|-------|----------|
| `id` | string | да | Уникальный ID товара |
| `category_id` | string | да | Ссылка на `categories.id` |
| `name` | string | да | Название на кнопке/карточке |
| `description` | string | нет | Подсказка (пока не в UI, резерв) |
| `price` | number | да | Цена в **рублях**, 2 знака после запятой |
| `currency` | string | нет | Всегда `RUB` |
| `stock` | integer | да | Остаток; **0** = нет в наличии |
| `unit` | string | да | `кг`, `л`, `шт`, `банка`, `пучок` и т.д. |
| `image_url` | string | нет | HTTPS URL фото; киоск кэширует локально |
| `is_active` | boolean | нет | `false` — не показывать (default: true) |
| `vat_code` | string | нет | Для чека: `none`, `vat0`, `vat10`, `vat20` — см. §7 |
| `updated_at` | string | нет | Время последнего изменения позиции |

### 4.1. Поведение киоска при остатках

| `stock` | Поведение UI |
|---------|----------------|
| `> 0` | Товар в сетке, можно добавить в корзину |
| `0` | Карточка с пометкой **«Нет в наличии»**, кнопки отключены |
| отсутствует в ответе | Киоск трактует как `999` (до уточнения контракта) |

### 4.2. Изображения

- URL должен быть доступен по **HTTPS** с NUC киоска.
- Рекомендуемый размер: **мин. 400×400 px**, JPG/WebP.
- Киоск сохраняет файл как `media/products/{id}.jpg`.
- При смене фото — тот же `id`, новый URL (киоск перекачает при 404/ETag — опционально в v2).

---

## 5. Резервирование / списание остатков (рекомендуется, фаза 2)

После успешной оплаты киоск может уведомлять CRM.

### `POST /orders`

**Тело:**
```json
{
  "kiosk_id": "kiosk-farm-01",
  "external_id": "a1b2c3d4",
  "payment_status": "paid",
  "payment_method": "card",
  "total": 1250.00,
  "currency": "RUB",
  "items": [
    {
      "product_id": "prod-1001",
      "name": "Клубника",
      "quantity": 2,
      "price": 450.00,
      "line_total": 900.00
    },
    {
      "product_id": "prod-1005",
      "name": "Молоко 3,2%",
      "quantity": 1,
      "price": 350.00,
      "line_total": 350.00
    }
  ],
  "paid_at": "2026-05-29T14:35:00+03:00"
}
```

| Поле | Описание |
|------|----------|
| `external_id` | UUID/короткий ID сессии киоска (для идемпотентности) |
| `payment_method` | `card`, `sbp`, `aqsi`, `mixed` |
| `items[].product_id` | ID из каталога |

**Ответ 201:**
```json
{
  "order_id": "crm-order-98765",
  "status": "accepted"
}
```

**Идемпотентность:** повтор `POST` с тем же `external_id` не должен дублировать списание.

> Если фаза 1 только каталог — эндпоинт можно отдать во второй итерации; киоск пока работает без него.

---

## 6. Опционально: один эндпоинт «снимок каталога»

Для упрощения CRM допускается объединённый метод:

### `GET /kiosk/catalog`

```json
{
  "categories": [ ... ],
  "products": [ ... ],
  "updated_at": "2026-05-29T14:00:00+03:00"
}
```

Киоск готов адаптировать `HttpCRMClient` под один или два эндпоинта — сообщите предпочтение.

---

## 7. Данные для фискализации (для чека aQsi / облака)

Для корректного чека желательно передавать в товаре (или отдельным справочником):

| Поле | Описание |
|------|----------|
| `vat_code` | Ставка НДС для позиции |
| `payment_object` | Признак предмета расчёта (товар, услуга) — при наличии в CRM |
| `marking` | Код маркировки «Честный знак» — если применимо |

Минимум для старта: **`vat_code`** или фиксированная ставка на стороне кассы.

---

## 8. Тестовый стенд

Просим предоставить:

| Параметр | Пример |
|----------|--------|
| Base URL (test) | `https://api-test.farm.example/v1` |
| API key (test) | отдельный ключ только для киоска |
| `kiosk_id` test | `kiosk-dev-01` |
| Пример curl | см. ниже |

```bash
curl -s -H "Authorization: Bearer TEST_KEY" \
  "https://api-test.farm.example/v1/health"

curl -s -H "Authorization: Bearer TEST_KEY" \
  "https://api-test.farm.example/v1/products?kiosk_id=kiosk-dev-01"
```

---

## 9. Конфигурация на стороне киоска

**Рекомендуется:** секреты в `.env` (см. [api/ENV.md](api/ENV.md)), не в git.

```env
CRM_API_BASE_URL=https://katushamarket.ru/api/v1
CRM_API_KEY=<ключ из ЛК CRM / Катюша>
CRM_KIOSK_ID=kiosk-farm-01
CRM_USE_MOCK=false
```

Дублирование в `config/settings.yaml` (без ключа):

```yaml
crm:
  base_url: "https://katushamarket.ru/api/v1"
  api_key: ""
  kiosk_id: "kiosk-farm-01"
  timeout_sec: 10
  use_mock: true
  catalog_mode: split
```

При наличии `CRM_API_KEY` в `.env` киоск автоматически использует HTTP-клиент (`HttpCRMClient`).

---

## 10. Контакты и согласование

| Вопрос | Ответственный |
|--------|----------------|
| Финальный список URL путей | CRM |
| OpenAPI/Swagger | CRM (желательно) |
| Тестовые ключи | CRM → команда киоска |
| Срок готовности test API | CRM |

**Со стороны киоска:** после получения Swagger/примера ответов — подключение `HttpCRMClient` в течение 1–2 рабочих дней.

---

## Приложение A: маппинг полей → код киоска

| JSON CRM | Класс Python |
|----------|----------------|
| `categories[].id` | `Category.id` |
| `categories[].name` | `Category.name` |
| `categories[].sort_order` | `Category.sort_order` |
| `products[].id` | `Product.id` |
| `products[].category_id` | `Product.category_id` |
| `products[].name` | `Product.name` |
| `products[].price` | `Product.price_rub` |
| `products[].stock` | `Product.stock` |
| `products[].unit` | `Product.unit` |
| `products[].image_url` | `Product.image_url` |
| `products[].description` | `Product.description` |
