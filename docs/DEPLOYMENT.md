# Деплой на NUC (киоск)

## Подготовка ПК

1. Windows 10 Pro, учётная запись только для киоска (рекомендуется).
2. Установить Python 3.11+ или собрать exe (отдельная задача — пока запуск из venv).
3. Клонировать репозиторий в **`C:\kiosk\`** (латиница в пути).
4. `pip install -r requirements.txt`, скопировать `config/settings.yaml` из example.
5. Выбрать пресет: `config/presets/mode_aqsi.yaml` → merge в `settings.yaml`.

## Сеть

См. [SETUP_NUC_PRINTER_LAN.md](SETUP_NUC_PRINTER_LAN.md) (режим 2) и [hardware/00-network-topology.md](hardware/00-network-topology.md).

- NUC: Wi‑Fi → интернет (CRM, облако).
- LAN: switch → принтер / POS / aQsi по IP из конфига.

## Kiosk-режим Windows

| Действие | Где |
|----------|-----|
| Fullscreen | `app.fullscreen: true` |
| Блок клавиш | `kiosk.block_keys: true` |
| Ctrl+Alt+Del | GPO / Assigned Access / Shell Launcher |
| Автозапуск | `scripts/install_autostart.ps1` или ярлык в `shell:startup` |

## Проверка перед выездом

Чеклист: [START_CHECKLIST.md](START_CHECKLIST.md).

1. `python main.py` — все экраны, сенсор.
2. Каталог: mock или боевой CRM.
3. Оплата: тестовый стенд банка (`use_mock: false` только с ключами).
4. Чек: aQsi или облако + принтер по режиму.
5. Логи: `logs/kiosk.log` без критических ошибок.

## Обновление на объекте

```powershell
cd C:\kiosk
git pull origin main
# перезапуск приложения
```

Секреты в `settings.yaml` / `.env` не перезаписывать при pull.

## Документы для монтажа

- Режим 1: [TBANK_REQUEST_MODE1.md](TBANK_REQUEST_MODE1.md)
- Режим 2: [SETUP_NUC_PRINTER_LAN.md](SETUP_NUC_PRINTER_LAN.md)
- CRM: [CRM_API_SPEC.md](CRM_API_SPEC.md)
