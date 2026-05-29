# Медиа и ассеты

## Демо-каталог (mock CRM)

Пока `crm.use_mock: true`, фото берутся из:

```
assets/demo_products/1.jpg … 12.jpg
```

Соответствие id → товар: см. `MockCRMClient.fetch_products()` в `src/services/crm_client.py`.

| id | Товар |
|----|--------|
| 1 | Клубника |
| 2 | Малина |
| 3 | Черника |
| 4 | Молоко 3,2% |
| 5 | Творог домашний |
| 6 | Сметана 20% |
| 7 | Мёд липовый |
| 8 | Мёд гречишный |
| 9 | Картофель |
| 10 | Морковь |
| 11 | Яйца С0 |
| 12 | Зелень укроп |

## Брендинг

```
assets/branding/farm_hero.jpg   # экран старта (~1080×600 в UI)
```

## Кэш CRM (боевой режим)

```
media/products/<product_id>.jpg
```

Скачивание: `CRMClient.download_image()` при `use_mock: false`.

В git: только `.gitkeep` в `media/products/` (сами фото не коммитятся).

## Генерация заглушек (Pillow)

```powershell
.\.venv\Scripts\python scripts\generate_product_images.py
```

Создаёт простые цветные плейсхолдеры — не путать с текущими AI-фото в репозитории.

## Размер файлов

Текущие JPEG ~2–2.7 МБ каждый. Для NUC при медленной загрузке меню — сжать до ~800 px по длинной стороне, quality 85.

## Загрузка в UI

Всегда через `load_pixmap()` из `src/ui/image_utils.py` — не использовать `QPixmap(path)` напрямую на Windows с кириллицей в пути.
