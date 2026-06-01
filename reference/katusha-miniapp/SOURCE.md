# Источник вёрстки

| Параметр | Значение |
|----------|----------|
| Оригинал | [https://699.ru/](https://699.ru/) — Telegram Mini App «Катюша — Фермерский маркет» |
| Канонический сайт | [https://katushamarket.ru](https://katushamarket.ru) (из meta) |
| Стек оригинала | Next.js, Tailwind CSS, `data-shop-surface="modern"` |
| Шрифты | **Unbounded** (заголовки), **Inter** (текст) |
| Акцент | `#3CB85D` (`manifest.theme_color`) |
| Ориентация | `portrait-primary` (manifest) |

## Что скопировано локально

| Файл | Описание |
|------|----------|
| `css/main1.css` | Оригинальные `@font-face` (Next) |
| `css/main2.css` | Оригинальный бандл Tailwind (~108 KB) — справочно |
| `css/tokens.css` | Извлечённые токены бренда |
| `css/layout.css` | Воспроизведение каталога для киоска |
| `index.html` + `js/app.js` | Статический прототип каталога |
| `assets/favicon.png`, `icon-512.png` | Иконки с 699.ru |

Полный React-бандл **не** включён (десятки chunk-файлов, нужен backend).  
Локальная копия — **референс UI** для переноса в PyQt6 (`theme.qss`).

## Открытие в браузере

```text
reference/katusha-miniapp/index.html
```

Превью под киоск 1080×1920:

```text
index.html?kiosk=1
```

## Правовое

Вёрстка принадлежит правообладателю «Катюша». Локальная копия — для внутренней разработки киоска заказчика, не для публикации как отдельный продукт.
