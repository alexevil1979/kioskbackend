# Катюша — локальная копия вёрстки mini app

Референс UI Telegram-магазина [699.ru](https://699.ru/) для переноса стиля в киоск PyQt6.

## Быстрый просмотр

Откройте в браузере:

`reference/katusha-miniapp/index.html`

Для масштаба под вертикальный киоск:

`index.html?kiosk=1`

## Структура

```
katusha-miniapp/
├── index.html          # Каталог: шапка, категории, сетка, корзина
├── css/
│   ├── tokens.css      # Цвета, шрифты, радиусы
│   ├── layout.css      # Компоненты
│   ├── main1.css       # Оригинал Next (шрифты)
│   └── main2.css       # Оригинал Next (Tailwind, справочно)
├── js/app.js           # Демо-корзина (12 товаров = mock киоска)
├── assets/             # favicon, icon-512
├── SOURCE.md           # Откуда снято
└── README.md
```

Фото товаров подтягиваются из `assets/demo_products/` киоска (относительный путь).

## Отличия от живого mini app

| Элемент | Оригинал 699.ru | Локальная копия |
|---------|-----------------|-----------------|
| Рендер | React / SSR | Статический HTML |
| Telegram SDK | `telegram-web-app.js` | Нет |
| Оплата, профиль, доставка | Есть | Нет (только каталог) |
| API товаров | Backend | Mock из `app.js` |

## Перенос в киоск PyQt6

См. [docs/design/KATUSHA_UI.md](../../docs/design/KATUSHA_UI.md):

- Заменить палитру `#3D7C2E` → `#3CB85D` в `theme.qss` (по согласованию)
- Шрифты: Unbounded / Inter (если лицензия позволяет на NUC)
- Нижняя панель: тёмный фон `#0F1115`, акцент зелёный
- Кнопки: `border-radius: 16px`, uppercase на CTA

## Обновление копии

При изменении дизайна на 699.ru:

1. Скачать заново `/_next/static/css/*.css`
2. Обновить `tokens.css` по новым hex из CSS
3. Подправить `layout.css` / скриншот в `docs/design/`
