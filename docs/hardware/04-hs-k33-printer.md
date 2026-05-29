# Kiosk Printer HS-K33 (HSPOS) — опционально

> **Статус:** не нужен при **aQsi 6** (встроенный принтер чеков).  
> Режим `legacy_umka` или отдельная нефискальная квитанция.

## По документации производителя

- Производитель: **HSPOS Technology** (hsprinter.com)
- Тип: встраиваемый киоск-принтер, **80 mm**, термопечать
- Скорость: до 180 mm/s
- Интерфейсы в базовой спецификации: **USB + RS232** (parallel опционально)
- ОС: Windows, Linux
- SDK: Windows C++/C#, Linux, Android, iOS — [страница загрузок](https://www.hsprinter.com/en/download.html)

Страница модели: [Kiosk Printer HS-K33](https://www.hsprinter.com/en/product/Kiosk-Printer-HS-K33.html)  
Руководство: «HS-K33 kiosk printer 80mm User Manual» — в разделе Download на сайте HSPOS.

## Расхождение со схемой объекта

В `киоск параметры.txt` указано: **HS-K33 → ethernet switch**.

У производителя для HS-K33 в паспорте **нет Ethernet** (в отличие от линейки HS-K21 с USB+Serial+**Ethernet**).

Возможные варианты на объекте:

1. Печать идёт **через УМКА** (фискальный чек), HS-K33 не используется по сети.
2. Принтер подключён к NUC по **USB**, а в схеме ошибочно указан switch.
3. Установлен **print server** / конвертер RS232/Ethernet.
4. Фактически другая модель (например HS-K21 с Ethernet).

**Нужно уточнение** — см. [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

## Если Ethernet подтверждён

Типичные варианты интеграции:

| Способ | Порт | Примечание |
|--------|------|------------|
| RAW TCP (ESC/POS) | 9100 | Проверить в утилите Printer Tools |
| Протопривный SDK HSPOS | — | DLL/SO из комплекта SDK |

В проекте: `src/services/printer_hs_k33.py`, настройки `hardware.printer.*`.

## Если USB к NUC

- Драйвер HSPOS для Windows
- Печать через spooler или SDK — `connection: usb` в конфиге

## Роль в процессе

| Сценарий | Принтер |
|----------|---------|
| Только 54‑ФЗ | Достаточно УМКА (своя или host-печать) |
| Дубль «заберите чек» крупным шрифтом | HS-K33 после успешного `fiscalcheck` |
