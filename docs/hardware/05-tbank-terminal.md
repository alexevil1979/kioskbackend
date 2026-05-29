# POS-терминал Т-Банк (PAX и др.)

> Для киоска без отдельной кассы предпочтительнее **[aQsi 6](07-tbank-aqsi.md)**.  
> Этот документ — для режима `tbank_pos_sbp` (PAX + Smart Sale).

## Подключение

**Wi‑Fi → интернет-роутер** или **Ethernet → switch**.

Для интеграции с киоском предпочтительно **Ethernet в ту же подсеть**, что LAN-порт NUC (см. [00-network-topology.md](00-network-topology.md)).

## Протокол для связи «киоск → терминал»

**INPAS Smart Sale** (Т-Банк называет технологию **Smart Sale** для связки касса↔терминал):

- Транспорт: **TCP/IP** (Ethernet или Wi‑Fi в LAN)
- Порт по умолчанию у многих интеграторов: **27015**
- Терминал должен быть в режиме Smart Sale / иметь прошивку с поддержкой протокола

Источники:

- [Т-Банк: касса и терминал](https://www.tbank.ru/business/help/business-payments/acquiring/online/integrate/)
- [Fusion POS: Smart Sale](https://docs.fusionpos.ru/smart-sale)
- [Restik: INPAS SmartSale на PAX/Verifone](https://help.restik.com/ru/articles/10774014)

## Фискализация без УМКА

При PAX чек пробивает **онлайн-касса из Т-Банка** (аренда aQsi, CloudKassir и др. — [список](https://www.tbank.ru/business/help/business-payments/acquiring/online/integrate/)), связанная с терминалом через Smart Sale или настройку банка.

УМКА на switch **не обязательна**.

## Настройка сети POS

1. DHCP на терминале + **резервация IP** в роутере (рекомендуется).
2. Или статический IP вне пула DHCP.
3. В `config/settings.yaml`: `hardware.tbank_terminal.host`, `port: 27015`.

## Реализация в проекте

- `src/services/payment_card.py` — заглушка; целевой модуль Smart Sale (DLL INPAS или TCP по спецификации от Т-Банка).
- Экран: `PaymentCardScreen` — «Следуйте инструкции на терминале…»

## Что запросить у Т-Банка

- [ ] Модель терминала (PAX A920, Verifone, …)
- [ ] Включён ли Smart Sale, IP и порт
- [ ] SDK / библиотека для Windows (INI, DLL, пример на C#/Python)
- [ ] Тестовый режим без списания
