# UI и экраны

## Портретный режим (основной)

- Разрешение: **1080 × 1920**
- Сетка товаров: **2 колонки**
- Категории: горизонтальная полоса в TopBar
- Стили: `src/ui/styles/theme.qss` + `theme_portrait.qss`
- Метрики: `src/ui/layout_metrics.py`

## Карточка товара (`ProductCard`)

| Состояние | UI |
|-----------|-----|
| В корзине 0 шт. | Кнопка **«Добавить»** |
| В корзине ≥ 1 | **−** · количество · **+** (кнопки `OutlineBtn`, 64×64 px в portrait) |
| Нет в наличии | Подпись «Нет в наличии», карточка disabled |

Фото: `src/ui/image_utils.py` (безопасно для путей с кириллицей).

## Навигация (`AppScreen`)

```
START → MENU ⇄ CART → PAYMENT_METHOD → PAYMENT_SBP | PAYMENT_CARD
                                              ↓
                                         SUCCESS → START
                                              ↓
                                    PAYMENT_ERROR / OFFLINE
```

Управление: `NavigationController` в `src/core/state_machine.py`, стек в `MainWindow`.

## Экраны (файлы)

| Экран | Файл |
|-------|------|
| Старт | `start_screen.py` |
| Меню | `menu_screen.py` |
| Корзина | `cart_screen.py` |
| Способ оплаты | `payment_method_screen.py` |
| СБП | `payment_sbp_screen.py` |
| Карта | `payment_card_screen.py` |
| Успех | `success_screen.py` |
| Ошибка / офлайн | `error_screens.py` |
| Бездействие | `widgets/idle_overlay.py` |

## Палитра (QSS)

- Фон: `#F5F0E6`
- Акцент: `#3D7C2E`, `#2D5016`
- Текст: `#2C2416`, `#5C4A32`

## Демо-контент

См. [ASSETS.md](ASSETS.md) — `assets/demo_products/`, `farm_hero.jpg`.
