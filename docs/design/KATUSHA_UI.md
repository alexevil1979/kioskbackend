# UI «Катюша» → киоск PyQt6

Связь с mini app [699.ru](https://699.ru/) и локальным референсом.

## Локальная вёрстка

**Путь:** [`reference/katusha-miniapp/`](../../reference/katusha-miniapp/)

| Файл | Назначение |
|------|------------|
| `index.html` | Интерактивный макет каталога |
| `css/tokens.css` | Дизайн-токены |
| `css/layout.css` | Компоненты |
| `SOURCE.md` | Источник и ограничения |

Открыть: `index.html` или `index.html?kiosk=1` (крупнее под 1080×1920).

## Дизайн-токены (из mini app)

| Токен | Значение | Киоск PyQt6 |
|-------|----------|-------------|
| Акцент | `#3CB85D` | `theme.qss` |
| Акцент тёмный | `#2D6A4F` | цена, outline |
| Фон страницы | `#F4F4F5` | `#Root` |
| Нижняя панель | `#0F1115` | `BottomBar` |
| Карточка | `#FFFFFF`, radius 20px | `ProductCard` |
| CTA | Unbounded, uppercase | `AddToCartBtn` / `CheckoutBtn` |
| Счётчик | border `#3CB85D` | `OutlineBtn` |

## Маппинг экранов

| Mini app (ожидаемо) | Киоск PyQt6 | Статус |
|---------------------|-------------|--------|
| Каталог + категории | `MenuScreen` | ✅ структура та же |
| Карточка товара | `ProductCard` | ✅ 1:1 с layout.css |
| Шапка + поиск | `KatushaHeader` | ✅ |
| Нижняя панель | `CartBottomBar` | ✅ «Оформить» |
| Корзина | `CartScreen` | ✅ |
| Оформление / оплата | `PaymentMethodScreen` + … | ✅ (логика киоска) |
| Старт / hero | `StartScreen` | ✅ свой hero «Ферма» → заменить на бренд Катюша? |

## План унификации стиля

1. **Фаза визуал** — обновить `theme.qss` / `theme_portrait.qss` по `tokens.css` (без смены логики).
2. **Фаза бренд** — логотип Катюша, `farm_hero` → баннер из mini app.
3. **Фаза данные** — единый каталог: CRM API = тот же backend, что 699.ru (уточнить у заказчика).

## Вопросы заказчику

1. Киоск и [699.ru](https://699.ru/) — **один** backend каталога?
2. Бренд на киоске: «Ферма» или «Катюша»?
3. Нижняя панель: тёмная как в mini app или оставить зелёную?

---

См. также: [../api/CRM_API_READINESS.md](../api/CRM_API_READINESS.md)
