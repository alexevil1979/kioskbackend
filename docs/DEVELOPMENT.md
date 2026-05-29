# Разработка

## Требования

- Windows 10/11 (целевая платформа киоска)
- Python 3.11+
- Git

## Первый запуск

```powershell
cd "c:\Users\1\Documents\киоск"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy config\settings.yaml.example config\settings.yaml
# отредактировать settings.yaml при необходимости
python main.py
```

**Рекомендация:** для продакшена путь к проекту только латиницей, например `C:\kiosk\` — меньше проблем с Qt и путями.

## Структура кода

```
main.py                 # точка входа
src/
  app.py                # QApplication, стили, сборка MainWindow
  core/                 # config, cart, navigation, idle, kiosk WinAPI
  models/               # Product, Category
  services/             # CRM, catalog, payment, fiscal, printer, aQsi
  ui/
    main_window.py      # оркестрация экранов и оплаты
    image_utils.py      # загрузка JPEG (кириллица в пути)
    layout_metrics.py   # portrait / landscape метрики
    screens/            # экраны
    widgets/            # ProductCard, BottomBar, кнопки
    styles/             # theme.qss, theme_portrait.qss
config/
  settings.yaml         # локально, в .gitignore
  settings.yaml.example
  presets/              # mode_aqsi, mode_pos_printer
assets/
  demo_products/        # 1.jpg … 12.jpg (демо)
  branding/             # farm_hero.jpg
media/products/         # кэш фото с CRM
logs/                   # kiosk.log
docs/                   # документация
scripts/
  generate_product_images.py
  install_autostart.ps1
  git-push.ps1
```

## Конфигурация разработчика

Для отладки без полного экрана в `config/settings.yaml`:

```yaml
app:
  fullscreen: false
  screen_width: 1080
  screen_height: 1920
  orientation: portrait

crm:
  use_mock: true

hardware:
  integration_mode: tbank_aqsi
```

Все платежи и касса — `use_mock: true` до получения ключей.

## Логи

- Файл: `logs/kiosk.log`
- Необработанные исключения дублируются через `sys.excepthook` в `src/app.py`

## Полезные команды

```powershell
# перегенерация простых заглушек Pillow (не AI)
.\.venv\Scripts\python scripts\generate_product_images.py

# push (см. GIT_WORKFLOW.md)
git add -A
git status
git commit -m "описание"
git push origin main
```

## Связанные документы

- [CONFIGURATION.md](CONFIGURATION.md) — все ключи `settings.yaml`
- [ARCHITECTURE.md](ARCHITECTURE.md) — классы и потоки
- [UI_AND_SCREENS.md](UI_AND_SCREENS.md) — экраны
- [GIT_WORKFLOW.md](GIT_WORKFLOW.md) — что не коммитить
