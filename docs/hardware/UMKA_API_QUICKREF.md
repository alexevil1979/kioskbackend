# УМКА HTTP API — краткая справка

Источник: [umki.org/knowledge-base/api-...](https://umki.org/knowledge-base/api-%d0%b4%d0%bb%d1%8f-%d1%80%d0%b0%d0%b1%d0%be%d1%82%d1%8b-%d1%81-%d0%ba%d0%ba%d0%bc-%d0%bd%d0%b0-%d0%bf%d0%bb%d0%b0%d1%82%d1%84%d0%be%d1%80%d0%bc%d0%b5-%d1%83%d0%bc%d0%ba%d0%b0/) (arMax / платформа УМКА).

## Базовый URL

```
http://<HOST>:<PORT>/
```

Тест (чужая касса): `http://office.armax.ru:58088/`

## Авторизация

```
Authorization: Basic base64(cashier_id:cashier_password)
```

## Проверка перед продажей

```http
GET /cashboxstatus.json
```

Смотреть: смена открыта, ФН не переполнен, `result == 0`, признаки бумаги.

## Открытие смены (при необходимости)

```http
GET /cycleopen.json?print=1
```

## Пробитие чека

```http
POST /fiscalcheck.json
Content-Type: application/json
```

Тело — объект `document` с `sessionId`, `print`, `data` (позиции в `fiscprops`, суммы в **копейках**, теги ФФД).  
Пример структуры в официальной документации (раздел «7. Печать чека»).

Минимально для киоска в запросе нужны:

- позиции (наименование, цена, количество, НДС);
- итог и тип оплаты (`moneyType`: наличные / безнал / и т.д.);
- признак расчёта (приход);
- email покупателя (опционально, тег 1008).

## Коды ошибок

- HTTP 4xx/5xx — транспорт/авторизация
- `result != 0` в JSON — ошибка ККТ (совместимость с кодами Атол, см. «Протокол ККТ 3.1.pdf» у поставщика)

## Связь с Т-Банк

УМКА **не в списке** «гарантированных» касс Т-Банка для готовой связки, но поддерживается протокол уровня HTTP API; связка с POS — через **Smart Sale** со стороны киоска/ middleware, не через облако Эвотор.

Список касс Т-Банка: [tbank.ru — интеграция кассы и терминала](https://www.tbank.ru/business/help/business-payments/acquiring/online/integrate/)
