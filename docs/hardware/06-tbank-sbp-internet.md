# СБП — оплата через интернет (Т‑Касса)

## Канал

**NUC Wi‑Fi → роутер → интернет** (не через switch).

СБП в киоске — это **не** QR на POS-терминале, а **интернет-эквайринг** Т-Банка (Т‑Касса):

- API: [developer.tbank.ru/eacq](https://developer.tbank.ru/eacq/api)
- Методы: `Init`, `GetQr` / payload для QR, `GetState` для polling
- Учётные данные: `TerminalKey` + пароль терминала из ЛК Т‑Бизнеса

## Поток в приложении

1. `PaymentInit` на сумму корзины.
2. Получение QR (ссылка или payload для генерации QR на экране).
3. Polling статуса до `CONFIRMED` / таймаут.
4. После успеха — `FiscalUmkaService.print_receipt()`.

## Библиотеки (справочно)

- Python: [tbank-securepay на PyPI](https://pypi.org/project/tbank-securepay/) (обёртка eacq API)

В проекте пока: `src/services/payment_sbp.py` (заглушка).

## Настройка

`config/settings.yaml`:

```yaml
payment:
  sbp:
    terminal_key: ""
    password: ""
    api_url: "https://securepay.tinkoff.ru/v2"
    use_mock: true
```

## Офлайн

Без интернета СБП недоступен → экран «Нет связи» или предложить оплату картой (если POS в LAN доступен).
