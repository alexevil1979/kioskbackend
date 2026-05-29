# Архитектура — основные классы

```
main.py
  └── src.app.run()
        ├── Settings (config.py)
        ├── CatalogStore ──► CRMClient (mock / http)
        ├── Cart
        ├── NavigationController (AppScreen enum)
        ├── IdleTimer
        ├── KeyboardBlocker (Windows)
        └── MainWindow (QStackedWidget)
              ├── StartScreen
              ├── MenuScreen + ProductCard + CartBottomBar
              ├── CartScreen
              ├── PaymentMethodScreen
              ├── PaymentSbpScreen
              ├── PaymentCardScreen
              ├── SuccessScreen
              ├── PaymentErrorScreen
              ├── OfflineScreen
              └── IdleWarningOverlay
```

## Поток оплаты (MVP)

`MENU → CART → PAYMENT_METHOD → (SBP|CARD) → SUCCESS → START`

Ошибки: `PAYMENT_ERROR`, офлайн: `OFFLINE`.

## Сигналы

- `Cart.changed` — обновление нижней панели и карточек
- `CatalogStore.updated` — перестройка категорий/сетки
- `NavigationController.screen_changed` — смена экрана
- `IdleTimer.warning / reset` — оверлей и полный сброс
