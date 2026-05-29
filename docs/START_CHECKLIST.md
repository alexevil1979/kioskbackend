# Старт проекта: два режима + что нужно

## Два режима (переключение в настройках)

Один параметр: `hardware.integration_mode` в `config/settings.yaml`.

| Режим | Значение | Железо | УМКА |
|-------|----------|--------|------|
| **1. aQsi «всё в одном»** | `tbank_aqsi` | NUC + **aQsi 6** (Т-Банк) | Не нужна |
| **2. POS + принтер** | `tbank_pos_printer` | NUC + **PAX** + **HS-K33** + облачная касса | Не нужна |

Опционально позже: `tbank_pos_sbp` — режим 2 + СБП QR на экране 32″.

### Пресеты конфига

**Режим 1 — aQsi:**
```yaml
hardware:
  integration_mode: tbank_aqsi
  aqsi:
    use_mock: false
    api_key: "..."   # из ЛК aQsi
  printer:
    enabled: false
fiscal:
  enabled: false
```

**Режим 2 — POS + принтер:**
```yaml
hardware:
  integration_mode: tbank_pos_printer
  tbank_terminal:
    host: "192.168.1.102"
    port: 27015
    smart_sale_enabled: true
    use_mock: false
  printer:
    enabled: true
    host: "192.168.1.101"
    port: 9100
  aqsi:
    use_mock: true
fiscal:
  enabled: true
  provider: cloudkassir
  use_mock: false
  cloud_public_id: "..."
  cloud_api_secret: "..."
```

---

## Что можно делать уже сейчас (без банка)

| Задача | Нужно от заказчика | Статус в проекте |
|--------|-------------------|------------------|
| UI, корзина, категории | — | Готово (mock CRM) |
| Kiosk fullscreen | NUC с Win10 | Готово |
| Переключение режимов | Выбор 1 или 2 | Готово в коде |
| Тест без железа | `use_mock: true` | Запуск `python main.py` |

```powershell
cd "c:\Users\1\Documents\киоск"
.\.venv\Scripts\activate
copy config\settings.yaml.example config\settings.yaml
python main.py
```

---

## Что требуется для **начала процесса** (реальные оплаты)

### Общее для обоих режимов

- [ ] **Юрлицо / ИП** с подключённым **Т-Бизнес** (расчётный счёт)
- [ ] **Торговый эквайринг** Т-Банка ([заявка](https://www.tbank.ru/business/payments/acquiring/terminal/))
- [ ] **CRM / каталог**: URL API, ключ, пример JSON товаров (или согласие на mock до запуска)
- [ ] **NUC** на объекте: Win10 Pro, 1920×1080, Wi‑Fi к роутеру
- [ ] **Роутер** с интернетом (CRM, облачная касса, обновления)
- [ ] Реквизиты для чека: ИНН, название, СНО, НДС, адрес расчётов
- [ ] Контакт техподдержки на объекте

### Режим 1 — `tbank_aqsi`

- [ ] Аренда/получение **aQsi 6** от Т-Банка
- [ ] **ФН** + регистрация кассы в ФНС (помощь Т-Банка)
- [ ] **API-ключ aQsi** (ЛК → Интеграции → внешний API)
- [ ] Письмо на **api@aqsi.ru**: киоск **без кассира**, автоприём заказа
- [ ] aQsi в той же Wi‑Fi сети, что NUC

### Режим 2 — `tbank_pos_printer`

- [ ] **POS** (PAX AF6 или модель из договора Т-Банка)
- [ ] **Smart Sale**: IP терминала, порт **27015**, **SDK** для Windows (запрос в Т-Бизнес 8 800 700-66-66)
- [ ] **HS-K33**: IP, порт печати (часто **9100**), рулоны **80 мм**, ⌀ до ~150 мм
- [ ] **Облачная касса**: CloudKassir или [Чеки Т-Бизнеса](https://www.tbank.ru/business/online-payments/cashreg/) + API-ключи
- [ ] NUC **LAN** на switch: принтер (+ опционально POS по кабелю)
- [ ] Расходники: лента **57 мм** для PAX, **80 мм** для HS-K33

---

## Порядок работ (рекомендуемый)

```
1. Выбор режима (1 или 2) + копия settings.yaml
2. Mock на NUC — обкатка UI и сценариев
3. Подключение эквайринга / устройств в Т-Бизнесе
4. Тестовая оплата 5–10 ₽ + проверка чека в ОФД
5. Подключение CRM (отключить crm.use_mock)
6. Выезд / приёмка на ферме
```

---

## Блокеры (без этого не идём в прод)

| Блокер | Режим |
|--------|--------|
| Нет API CRM | оба |
| Нет эквайринга | оба |
| aQsi: нет API / нет unattended | 1 |
| POS: нет Smart Sale SDK | 2 |
| Нет облачной кассы + ключей | 2 |
| Принтер: неизвестен IP / не Ethernet | 2 |

---

## Документы

- [00-architecture-tbank-first.md](hardware/00-architecture-tbank-first.md)
- [07-tbank-aqsi.md](hardware/07-tbank-aqsi.md)
- [08-tbank-pos-printer.md](hardware/08-tbank-pos-printer.md)
- [OPEN_QUESTIONS.md](hardware/OPEN_QUESTIONS.md)
