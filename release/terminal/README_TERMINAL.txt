САДЫ КОЛОМНЫ — КИОСК (Windows 10)
==================================

БЫСТРЫЙ СТАРТ
-------------
1. Распакуйте архив в C:\kiosk  (путь только латиницей).
2. Установите Python 3.11+ с python.org (галочка «Add to PATH»).
3. PowerShell в папке киоска:

   Set-ExecutionPolicy -Scope Process Bypass -Force
   .\install.ps1 -Autostart

4. Заполните config\settings.yaml и .env (ключи API, IP принтера/терминала).
5. Запуск: run_kiosk.bat  или перезагрузка (если включён автозапуск).

ПОДРОБНАЯ ИНСТРУКЦИЯ
--------------------
docs\INSTALL_TERMINAL_WIN10.md

ОБНОВЛЕНИЕ
----------
Вариант A — с интернетом (GitHub, ветка main):

   update_kiosk.bat

Скрипт скачает архив с GitHub и развернёт в C:\kiosk.
Сохраняются config\settings.yaml, .env, logs\, media\products\.

Вариант B — вручную:

Распакуйте новый ZIP поверх C:\kiosk (не затирайте settings.yaml и .env),
затем снова: .\install.ps1

ПОДДЕРЖКА
---------
Логи: logs\kiosk.log
Репозиторий: https://github.com/alexevil1979/kioskbackend
