# Готовность API для работы киоска

**Дата анализа:** 2026-05-29  
**Спецификация:** [crm/CRM_API_SPEC.md](crm/CRM_API_SPEC.md) v1.0  
**Код:** `src/services/crm_client.py`, `catalog_sync.py`

Документ отвечает на вопрос: **что уже описано и реализовано, чего не хватает**, чтобы киоск мог работать на объекте (каталог → корзина → оплата → учёт).

---

## Сводка (одним взглядом)

| Область | В спецификации | В коде киоска | От CRM (внешне) | Критичность |
|---------|----------------|---------------|-----------------|-------------|
| Health / online | ✅ | ✅ частично | Нужен реальный URL | **Блокер фазы 1** |
| Категории | ✅ | ❌ NotImplemented | Нужен эндпоинт | **Блокер фазы 1** |
| Товары + остатки | ✅ | ❌ NotImplemented | Нужен эндпоинт | **Блокер фазы 1** |
| Фото (CDN URL) | ✅ | ✅ загрузка есть | HTTPS с NUC | **Блокер фазы 1** |
| Кэш offline | ✅ (поведение) | ✅ | — | Готово |
| Заказ POST /orders | ✅ фаза 2 | ❌ нет | Желательно | Средняя |
| vat_code для чека | ✅ опционально | ❌ в Product | Желательно | Средняя |
| OpenAPI / test keys | запрошено | — | Не получено | **Блокер интеграции** |
| Оплата aQsi | вне CRM | ✅ mock | Ключи Т-Банк | Отдельный трек |
| СБП QR | вне CRM | ✅ mock | API банка | Опционально |

**Сейчас киоск полностью работает только с `crm.use_mock: true`.**  
Для боевого каталога нужны **реальный API CRM + доработка `HttpCRMClient`**.

---

## 1. Что есть в спецификации CRM (описано)

### 1.1. Обязательный минимум (фаза 1 — каталог)

| Метод | Путь | Назначение для киоска |
|-------|------|------------------------|
| `GET` | `/health` | Проверка связи, `CatalogStore.is_online()` |
| `GET` | `/categories` | Верхняя панель категорий |
| `GET` | `/products` | Сетка товаров, цены, остатки |

**Альтернатива:** один `GET /kiosk/catalog` (категории + товары) — киоск готов под любой вариант.

### 1.2. Общие правила (описаны)

- HTTPS, JSON UTF-8, Bearer token, `X-Kiosk-Id`
- Таймаут ≤ 10 с, polling 15–30 с
- Коды 401/429/5xx и поведение offline на кэше
- Поля товара: `id`, `category_id`, `name`, `price`, `stock`, `unit`, `image_url`, `is_active`
- Поведение при `stock = 0` → «Нет в наличии»

### 1.3. Фаза 2 (рекомендуется)

| Метод | Путь | Назначение |
|-------|------|------------|
| `POST` | `/orders` | Списание остатков в CRM после оплаты, идемпотентность по `external_id` |

### 1.4. Для чеков (aQsi / облако)

- `vat_code` на товаре (`none`, `vat0`, `vat10`, `vat20`)
- Опционально: `payment_object`, маркировка

### 1.5. Примеры в репозитории

| Файл | Содержание |
|------|------------|
| [examples/health.response.json](examples/health.response.json) | Health |
| [examples/categories.response.json](examples/categories.response.json) | Категории |
| [examples/products.response.json](examples/products.response.json) | Товары |
| [examples/order.request.json](examples/order.request.json) | Заказ после оплаты |

---

## 2. Что реализовано в киоске (код)

### 2.1. Готово

| Компонент | Файл | Статус |
|-----------|------|--------|
| Mock-каталог (12 товаров) | `MockCRMClient` | ✅ Работает |
| Polling каталога | `CatalogStore` | ✅ 15–30 с |
| Offline на кэше | `CatalogStore.refresh()` | ✅ При сбое API остаётся последний каталог |
| Скачивание фото | `CRMClient.download_image()` | ✅ В `media/products/{id}.jpg` |
| Заголовки Bearer + X-Kiosk-Id | `HttpCRMClient.__init__` | ✅ |
| Health (заготовка) | `HttpCRMClient.is_online()` | ✅ Вызов `/health` |
| UI: категории, сетка, остатки | `MenuScreen`, `ProductCard` | ✅ |
| Конфиг `crm.*` | `config/settings.yaml.example` | ✅ `kiosk_id`, `use_mock` |

### 2.2. Не реализовано (нужно после API CRM)

| Задача | Файл | Оценка |
|--------|------|--------|
| Парсинг `GET /categories` | `HttpCRMClient.fetch_categories` | 2–4 ч |
| Парсинг `GET /products` или `/kiosk/catalog` | `HttpCRMClient.fetch_products` | 4–6 ч |
| Фильтр `is_active == false` | при парсинге | 1 ч |
| Поле `vat_code` в `Product` | `models/product.py` + чек | 2–4 ч |
| `POST /orders` после успешной оплаты | новый метод + `main_window` | 4–8 ч |
| `updated_since` (инкремент) | опционально v2 | 4–8 ч |
| ETag / перекачка фото | опционально v2 | 4 ч |

`HttpCRMClient` сейчас при `use_mock: false` **упадёт** на `NotImplementedError` при обновлении каталога.

---

## 3. Чего не хватает от CRM (внешние блокеры)

Без этого киоск **не переключится** на боевой каталог.

| # | Что нужно | Зачем киоску |
|---|-----------|--------------|
| 1 | **Base URL** test + prod | `crm.base_url` |
| 2 | **API key** (Bearer) | авторизация |
| 3 | **`kiosk_id`** точки | цены/остатки этой точки |
| 4 | Рабочие **`GET /health`**, **`/categories`**, **`/products`** (или `/kiosk/catalog`) | каталог |
| 5 | **Пример реального JSON** или **OpenAPI** | быстрая реализация `HttpCRMClient` |
| 6 | **CDN фото** доступен с IP киоска (HTTPS) | карточки товаров |
| 7 | Согласование **путей** (`/api/v1/...` vs `/v1/...`) | один раз в конфиге |

Желательно на фазе 2:

| # | Что нужно | Зачем |
|---|-----------|-------|
| 8 | `POST /orders` + идемпотентность | остатки в CRM |
| 9 | `vat_code` в товарах | корректный чек aQsi/облако |
| 10 | Webhook «остаток изменился» | вместо только polling (v2) |

---

## 4. Чего не хватает вне CRM (но нужно для «полного» киоска)

Эти API **не входят** в CRM_API_SPEC — отдельные интеграции.

| Система | Для чего | Статус в проекте | Документ |
|---------|----------|------------------|----------|
| **aQsi Cloud API** | Режим 1: оплата + чек на терминале | Mock, нужен ключ + unattended | [hardware/07-tbank-aqsi.md](../hardware/07-tbank-aqsi.md) |
| **Т-Банк POS / Smart Sale** | Режим 2: оплата картой | Mock | [hardware/05-tbank-terminal.md](../hardware/05-tbank-terminal.md) |
| **CloudKassir / Чеки Т-Бизнеса** | Режим 2: фискализация | Mock | [hardware/08-tbank-pos-printer.md](../hardware/08-tbank-pos-printer.md) |
| **СБП (Tinkoff v2 и др.)** | QR на экране 32″ | Mock | [hardware/06-tbank-sbp-internet.md](../hardware/06-tbank-sbp-internet.md) |
| **HS-K33 ESC/POS** | Бумажная копия (режим 2) | Заготовка LAN | [hardware/04-hs-k33-printer.md](../hardware/04-hs-k33-printer.md) |

**Основной режим заказчика:** `tbank_aqsi` — CRM нужен в первую очередь для **каталога и остатков**; оплата идёт через aQsi, не через CRM.

---

## 5. Матрица: сценарий киоска → нужный API

| Шаг пользователя | Нужен CRM API? | Нужна оплата/чек? | Сейчас |
|------------------|----------------|-------------------|--------|
| Старт → Меню | Да (каталог) | — | Mock |
| Выбор товара | Да (цена, stock) | — | Mock |
| Корзина | Локально | — | ✅ |
| Оплата | Нет* | aQsi / POS / СБП | Mock |
| Успех | Желательно `POST /orders` | Чек на aQsi/облаке | Чек mock, CRM заказ нет |
| Нет сети | Кэш каталога | — | ✅ логика есть |
| Обновление цен | Polling products | — | Ждёт CRM |

\* СБП через backend CRM возможен в будущем — в текущей спецификации **не описан**.

---

## 6. Рекомендуемый порядок внедрения

### Этап A — «Киоск видит витрину» (минимум)

1. CRM отдаёт test API + ключи.  
2. Реализовать `HttpCRMClient` (health + categories + products).  
3. `crm.use_mock: false` на dev-NUC.  
4. Проверить фото, остатки, offline.

### Этап B — «Оплата на объекте»

1. aQsi: API key, режим unattended (Т-Банк).  
2. `hardware.aqsi.use_mock: false`.  
3. Прогон: корзина → терминал → чек.

### Этап C — «Учёт в CRM»

1. `POST /orders` в CRM.  
2. Вызов из `_finish_payment_success()` в `main_window.py`.  
3. `vat_code` в позициях чека.

---

## 7. Чеклист согласования с разработчиками CRM

Перед стартом интеграции передайте им [crm/CRM_API_SPEC.md](crm/CRM_API_SPEC.md) и попросите отметить:

- [ ] Финальный base path (`/v1` / `/api/v1`)
- [ ] Один или два эндпоинта каталога
- [ ] Формат `id` товара (строка, стабильность)
- [ ] Поведение при отсутствии `stock` в JSON
- [ ] URL фото: постоянные или с подписью/TTL
- [ ] Срок готовности test-стенда
- [ ] План по `POST /orders` (дата фазы 2)

---

## 8. Связанные документы

- [QUESTIONS.md](../QUESTIONS.md) — вопросы заказчику  
- [STATUS.md](../STATUS.md) — статус проекта  
- [DEVELOPMENT.md](../DEVELOPMENT.md) — запуск и конфиг  
- [../CRM_API_SPEC.md](../CRM_API_SPEC.md) — копия для передачи CRM (корень docs)
