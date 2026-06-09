# Установка киоска на терминал (Windows 10)

Инструкция для выезда на объект: NUC / сенсорный ПК с Windows 10 Pro, экран 32″ (1080×1920).

---

## 1. Что понадобится

| Компонент | Требование |
|-----------|------------|
| ОС | Windows 10 Pro (64-bit) |
| Python | **3.11 или новее** ([python.org](https://www.python.org/downloads/windows/)) |
| Место на диске | ~500 МБ (ПО + venv + кэш картинок) |
| Сеть | Wi‑Fi или Ethernet с интернетом (CRM, СБП) |
| Архив | `dist/kiosk-terminal-YYYYMMDD.zip` (собирается на dev-ПК) |

На терминале **не нужен** Git — только распакованный архив.

---

## 2. Сборка пакета (на dev-ПК)

В корне репозитория:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_terminal_package.ps1
```

Результат:

- `dist/kiosk-terminal-YYYYMMDD/` — папка для копирования
- `dist/kiosk-terminal-YYYYMMDD.zip` — **этот файл везите на терминал** (флешка / AnyDesk / сеть)

В архив **не входят**: `.env`, `config/settings.yaml`, логи, кэш `media/products` — они создаются на месте.

---

## 3. Подготовка терминала

### 3.1. Папка установки

Распакуйте ZIP в:

```
C:\kiosk
```

Путь **только латиницей** (без кириллицы и пробелов).

### 3.2. Python

1. Скачайте **Windows installer (64-bit)** Python 3.11+.
2. При установке включите **«Add python.exe to PATH»**.
3. Проверка в PowerShell:

```powershell
py -3 --version
```

Должно быть `Python 3.11.x` или выше.

### 3.3. Windows (рекомендуется)

- Отдельная учётная запись «Kiosk» без лишних прав.
- Отключить сон / гибернацию на время работы.
- Отложить автоматические перезагрузки Windows в часы работы.
- Разрешить исходящий HTTPS (443) для CRM и платёжных API.

---

## 4. Установка ПО киоска

PowerShell **в папке `C:\kiosk`**:

```powershell
cd C:\kiosk
Set-ExecutionPolicy -Scope Process Bypass -Force
.\install.ps1 -Autostart
```

Скрипт:

1. Создаёт `.venv` и ставит зависимости из `requirements.txt`
2. Копирует `config/settings.yaml.example` → `config/settings.yaml` (если файла ещё нет)
3. Копирует `.env.example` → `.env` (если файла ещё нет)
4. Создаёт `logs/`, `media/products/`
5. С `-Autostart` — ярлык в автозагрузке Windows (`pythonw`, без консоли)

Без автозапуска (только venv):

```powershell
.\install.ps1
```

---

## 5. Настройка перед первым запуском

### 5.1. `config/settings.yaml`

Минимум для боевого киоска Kolomna:

```yaml
app:
  title: "Сады Коломны — киоск"
  ui_theme: kolomna
  fullscreen: true
  dev_mode: false
  screen_width: 1080
  screen_height: 1920

crm:
  use_mock: false
  kiosk_id: "kiosk-farm-01"

hardware:
  integration_mode: tbank_pos_sbp   # или tbank_aqsi / tbank_pos_printer
  printer:
    enabled: true
    host: "192.168.10.20"          # IP принтера HS-K33
    port: 9100
  tbank_terminal:
    host: "192.168.10.30"
    port: 27015
    use_mock: false
```

Полный пример — `config/settings.yaml.example`.  
Подробнее: [CONFIGURATION.md](CONFIGURATION.md).

### 5.2. Пресеты режима оплаты

В пакете есть `config/presets/`:

| Файл | Режим |
|------|--------|
| `mode_pos_sbp.yaml` | СБП QR на экране + карта на POS |
| `mode_aqsi.yaml` | aQsi 6 (всё на терминале) |
| `mode_pos_printer.yaml` | POS + принтер + облачная касса |

Скопируйте нужные секции в `config/settings.yaml` вручную.

### 5.3. `.env` (секреты)

```env
KIOSK_API_KEY=ваш_ключ
KIOSK_API_BASE_URL=https://admin.katushamarket.ru/api/external/kiosk
CRM_USE_MOCK=false
PAYMENT_SBP_USE_MOCK=false
INTEGRATION_MODE=tbank_pos_sbp
```

См. [.env.example](../.env.example) и [api/ENV.md](api/ENV.md).

---

## 6. Запуск и проверка

| Способ | Команда |
|--------|---------|
| С консолью (отладка) | `run_kiosk.bat` |
| Без консоли | `run_kiosk_silent.bat` |
| Автозапуск | перезагрузка ПК (после `install.ps1 -Autostart`) |

### Чеклист приёмки

1. Заставка / категории / меню / корзина — сенсор откликается.
2. Каталог подгружается (или mock, если API недоступен).
3. Тестовая оплата по сценарию заказчика.
4. Лог `logs/kiosk.log` без критических ошибок.
5. Таймер бездействия: через ~50 с — «Вы ещё здесь?».

Полный чеклист: [START_CHECKLIST.md](START_CHECKLIST.md).

---

## 7. Сеть (принтер по LAN)

Если принтер HS-K33 в отдельной подсети через switch — см. [SETUP_NUC_PRINTER_LAN.md](SETUP_NUC_PRINTER_LAN.md).

Типовая схема:

- Wi‑Fi NUC → интернет (CRM, СБП)
- Ethernet NUC → switch → принтер `192.168.10.20`, POS `192.168.10.30`

---

## 8. Автозапуск

Создать:

```powershell
.\install_autostart.ps1
```

Удалить:

```powershell
.\uninstall_autostart.ps1
```

Ярлык: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SadyKolomnyKiosk.lnk`

---

## 9. Обновление на объекте

1. Остановите киоск (закройте окно или завершите `pythonw` в диспетчере задач).
2. Сохраните копии `config/settings.yaml` и `.env`.
3. Распакуйте новый ZIP **поверх** `C:\kiosk` (не затирайте settings и .env).
4. Снова выполните:

```powershell
cd C:\kiosk
.\install.ps1
```

5. Верните settings/.env, если перезаписались.
6. Запустите `run_kiosk.bat` и проверьте экраны.

---

## 10. Устранение неполадок

| Симптом | Действие |
|---------|----------|
| «Python не найден» | Переустановить Python с PATH; перезайти в Windows |
| Чёрный экран / нет UI | Запустить `run_kiosk.bat` — смотреть ошибку в консоли |
| Нет каталога | Проверить `KIOSK_API_KEY`, интернет, `logs/kiosk.log` |
| Не печатает чек | `ping` на IP принтера; `hardware.printer` в settings |
| Квадрат в углу экрана | Перезапуск после обновления; проверить idle-оверлей |
| Автозапуск не срабатывает | `install_autostart.ps1`; путь `C:\kiosk` без кириллицы |

Логи: `C:\kiosk\logs\kiosk.log`

---

## 11. Структура пакета

```
C:\kiosk\
  main.py
  requirements.txt
  run_kiosk.bat
  run_kiosk_silent.bat
  install.ps1
  install_autostart.ps1
  README_TERMINAL.txt
  .env.example
  config\
    settings.yaml.example
    presets\
  src\
  assets\
  docs\
    INSTALL_TERMINAL_WIN10.md
  logs\
  media\products\
  .venv\          ← создаётся install.ps1
```

---

## Связанные документы

- [DEPLOYMENT.md](DEPLOYMENT.md) — общий деплой NUC
- [CONFIGURATION.md](CONFIGURATION.md) — все параметры
- [hardware/02-nuc-kiosk-pc.md](hardware/02-nuc-kiosk-pc.md) — железо NUC
