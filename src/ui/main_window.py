from __future__ import annotations

import logging
import random
import uuid
from typing import TYPE_CHECKING

from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget, QWidget

from src.core.cart import Cart
from src.core.config import Settings
from src.core.idle_timer import IdleTimer
from src.core.state_machine import AppScreen, NavigationController
from src.services.catalog_sync import CatalogStore
from src.services.fiscal_cloud import CloudFiscalService
from src.services.fiscal_umka import FiscalUmkaService
from src.services.payment_card import CardPaymentService
from src.services.payment_sbp import SbpPaymentService
from src.services.printer_hs_k33 import PrinterHsK33Service
from src.services.tbank_aqsi import AqsiOrderService
from src.ui.screens.cart_screen import CartScreen
from src.ui.screens.error_screens import OfflineScreen, PaymentErrorScreen
from src.ui.screens.menu_screen import MenuScreen
from src.ui.screens.payment_card_screen import PaymentCardScreen
from src.ui.screens.payment_method_screen import PaymentMethodScreen
from src.ui.screens.payment_sbp_screen import PaymentSbpScreen
from src.ui.screens.start_screen import StartScreen
from src.ui.screens.success_screen import SuccessScreen
from src.ui.widgets.idle_overlay import IdleWarningOverlay

if TYPE_CHECKING:
    from src.core.kiosk_win import KeyboardBlocker

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(
        self,
        settings: Settings,
        catalog: CatalogStore,
        cart: Cart,
        nav: NavigationController,
        idle: IdleTimer,
        keyboard: KeyboardBlocker | None = None,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._catalog = catalog
        self._cart = cart
        self._nav = nav
        self._idle = idle
        self._keyboard = keyboard
        self._order_id = ""
        self._last_payment: str = "sbp"
        self._aqsi_order_id = ""
        self._aqsi_polls = 0

        hw = settings.hardware
        self._sbp = SbpPaymentService()
        self._card = CardPaymentService(settings.payment, hw.tbank_terminal)
        self._aqsi = AqsiOrderService(hw.aqsi)
        self._fiscal_umka = FiscalUmkaService(settings)
        self._fiscal_cloud = CloudFiscalService(settings.fiscal)
        self._printer = PrinterHsK33Service(hw.printer)

        self.setWindowTitle(settings.app.title)
        self.setObjectName("Root")

        central = QWidget()
        self.setCentralWidget(central)
        self._stack = QStackedWidget(central)
        from PyQt6.QtWidgets import QVBoxLayout

        lay = QVBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._stack)

        self._screens: dict[AppScreen, QWidget] = {}
        self._register_screens()
        self._idle_overlay = IdleWarningOverlay(central)

        nav.screen_changed.connect(self._on_screen_changed)
        idle.warning.connect(self._idle_overlay.show_overlay)
        idle.reset.connect(self._on_idle_reset)
        self._idle_overlay.stay.connect(idle.dismiss_warning)
        self._idle_overlay.leave.connect(self._full_reset)

        catalog.offline_changed.connect(self._on_offline)
        catalog.refresh()

        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app:
            app.installEventFilter(self)

        self._apply_kiosk_geometry()
        self._nav.reset_to_start()

    def _register_screens(self) -> None:
        s = self._settings
        start = StartScreen(s)
        start.tapped.connect(lambda: self._nav.go(AppScreen.MENU))

        menu = MenuScreen(self._catalog, self._cart, s)
        menu.go_cart.connect(lambda: self._nav.go(AppScreen.CART))
        menu.restart.connect(self._confirm_restart)

        cart = CartScreen(self._cart, s)
        cart.continue_shopping.connect(lambda: self._nav.go(AppScreen.MENU))
        cart.pay.connect(self._go_payment)

        pay_method = PaymentMethodScreen()
        pay_method.sbp_selected.connect(self._start_sbp)
        pay_method.card_selected.connect(self._start_card)
        pay_method.cancel.connect(lambda: self._nav.go(AppScreen.CART))

        sbp = PaymentSbpScreen(s.payment.sbp_timeout_sec)
        sbp.cancel.connect(self._cancel_sbp)
        sbp.failed.connect(self._payment_failed)

        card_scr = PaymentCardScreen()
        card_scr.cancel.connect(self._cancel_card)
        card_scr.completed.connect(self._on_card_completed)

        success = SuccessScreen()
        err = PaymentErrorScreen()
        err.retry.connect(lambda: self._nav.go(AppScreen.PAYMENT_METHOD))
        err.to_menu.connect(self._full_reset)

        offline = OfflineScreen()
        offline.retry.connect(self._catalog.refresh)

        mapping = {
            AppScreen.START: start,
            AppScreen.MENU: menu,
            AppScreen.CART: cart,
            AppScreen.PAYMENT_METHOD: pay_method,
            AppScreen.PAYMENT_SBP: sbp,
            AppScreen.PAYMENT_CARD: card_scr,
            AppScreen.SUCCESS: success,
            AppScreen.PAYMENT_ERROR: err,
            AppScreen.OFFLINE: offline,
        }
        for screen, widget in mapping.items():
            self._screens[screen] = widget
            self._stack.addWidget(widget)

    def _apply_kiosk_geometry(self) -> None:
        if self._settings.app.fullscreen:
            self.showFullScreen()
        else:
            self.resize(self._settings.app.screen_width, self._settings.app.screen_height)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

    def _on_screen_changed(self, screen: AppScreen) -> None:
        widget = self._screens.get(screen)
        if widget:
            self._stack.setCurrentWidget(widget)
        self._idle.bump()
        if screen == AppScreen.PAYMENT_METHOD:
            pm = self._screens[AppScreen.PAYMENT_METHOD]
            assert isinstance(pm, PaymentMethodScreen)
            pm.set_amount(self._cart.total_display())
        if screen in (AppScreen.PAYMENT_SBP, AppScreen.PAYMENT_CARD):
            self._idle.pause()
        else:
            self._idle.resume()
        logger.info("Экран: %s", screen.name)

    def _go_payment(self) -> None:
        if self._catalog.is_offline:
            self._nav.go(AppScreen.OFFLINE)
            return
        if self._cart.positions_count == 0:
            return
        self._order_id = str(uuid.uuid4())[:8]
        mode = self._settings.hardware.integration_mode
        if mode == "tbank_aqsi":
            self._start_aqsi_payment()
        elif mode in ("tbank_pos_printer", "tbank_pos_sbp"):
            self._nav.go(AppScreen.PAYMENT_METHOD)
        else:
            self._nav.go(AppScreen.PAYMENT_METHOD)

    def _start_aqsi_payment(self) -> None:
        """Т-Банк aQsi: заказ в облако → оплата и чек на терминале."""
        self._last_payment = "aqsi"
        result = self._aqsi.create_order(self._cart.lines, self._cart.total_rub, self._order_id)
        if not result.success:
            logger.error("aQsi: %s", result.error)
            self._payment_failed()
            return
        self._aqsi_order_id = result.order_id
        card_scr = self._screens[AppScreen.PAYMENT_CARD]
        assert isinstance(card_scr, PaymentCardScreen)
        card_scr.set_instruction(
            "Оплата на терминале Т-Банка",
            "Заказ отправлен на aQsi.\n"
            "Оплатите картой или QR на терминале рядом с киоском.",
            "Ожидание оплаты…",
        )
        self._nav.go(AppScreen.PAYMENT_CARD)
        card_scr.start_waiting(mock_auto_success=False)
        self._aqsi_polls = 0
        self._poll_aqsi_payment()

    def _poll_aqsi_payment(self) -> None:
        cfg = self._settings.hardware.aqsi
        if self._nav.current != AppScreen.PAYMENT_CARD:
            return
        status = self._aqsi.poll_order_status(self._aqsi_order_id)
        if status in ("paid", "completed", "success", "closed"):
            self._on_card_completed(True)
            return
        if status in ("failed", "cancelled", "canceled", "error"):
            self._on_card_completed(False)
            return
        self._aqsi_polls += 1
        max_polls = max(1, cfg.poll_max_sec // cfg.poll_interval_sec)
        if self._aqsi_polls >= max_polls:
            self._on_card_completed(False)
            return
        if cfg.use_mock and self._aqsi_polls >= 3:
            self._on_card_completed(True)
            return
        QTimer.singleShot(cfg.poll_interval_sec * 1000, self._poll_aqsi_payment)

    def _start_sbp(self) -> None:
        self._last_payment = "sbp"
        session = self._sbp.create_payment(self._cart.total_rub, self._order_id)
        sbp_scr = self._screens[AppScreen.PAYMENT_SBP]
        assert isinstance(sbp_scr, PaymentSbpScreen)
        self._nav.go(AppScreen.PAYMENT_SBP)
        sbp_scr.start_payment(session.qr_payload, session.payment_id)
        # Dev: двойной тап по QR имитирует оплату — пока mock polling
        QTimer.singleShot(8000, self._mock_sbp_paid)

    def _mock_sbp_paid(self) -> None:
        if self._nav.current == AppScreen.PAYMENT_SBP:
            self._finish_payment_success()

    def _cancel_sbp(self) -> None:
        sbp_scr = self._screens[AppScreen.PAYMENT_SBP]
        if isinstance(sbp_scr, PaymentSbpScreen):
            sbp_scr.stop()
        self._nav.go(AppScreen.PAYMENT_METHOD)

    def _start_card(self) -> None:
        self._last_payment = "card"
        result = self._card.pay(self._cart.total_rub, self._order_id)
        if not result.success:
            self._payment_failed()
            return
        card_scr = self._screens[AppScreen.PAYMENT_CARD]
        assert isinstance(card_scr, PaymentCardScreen)
        self._nav.go(AppScreen.PAYMENT_CARD)
        card_scr.start_waiting(mock_auto_success=self._settings.hardware.tbank_terminal.use_mock)

    def _cancel_card(self) -> None:
        card_scr = self._screens[AppScreen.PAYMENT_CARD]
        if isinstance(card_scr, PaymentCardScreen):
            card_scr.stop()
        self._nav.go(AppScreen.PAYMENT_METHOD)

    def _on_card_completed(self, success: bool) -> None:
        card_scr = self._screens[AppScreen.PAYMENT_CARD]
        if isinstance(card_scr, PaymentCardScreen):
            card_scr.stop()
        if success:
            self._finish_payment_success()
        else:
            self._payment_failed()

    def _finish_payment_success(self) -> None:
        sbp_scr = self._screens.get(AppScreen.PAYMENT_SBP)
        if isinstance(sbp_scr, PaymentSbpScreen):
            sbp_scr.stop()
        mode = self._settings.hardware.integration_mode
        if mode == "tbank_aqsi":
            logger.info("aQsi: оплата и фискализация на терминале Т-Банка")
        elif mode in ("tbank_pos_printer", "tbank_pos_sbp"):
            cloud = self._fiscal_cloud.print_receipt(
                self._cart.lines,
                self._cart.total_rub,
                self._last_payment,
                self._order_id,
            )
            if not cloud.success:
                logger.error("Облачный фискальный чек: %s", cloud.error)
            if self._settings.hardware.printer.enabled:
                self._printer.print_order_slip(
                    self._cart.lines, self._cart.total_rub, self._order_id
                )
            else:
                logger.warning("Принтер HS-K33 отключён — бумажной копии не будет")
        elif mode == "legacy_umka":
            fiscal = self._fiscal_umka.print_receipt(
                self._cart.lines, self._cart.total_rub, self._last_payment
            )
            if not fiscal.success:
                logger.error("Ошибка чека УМКА: %s", fiscal.error)
            elif self._settings.hardware.printer.enabled:
                self._printer.print_order_slip(
                    self._cart.lines, self._cart.total_rub, self._order_id
                )
        else:
            logger.info("Неизвестный integration_mode=%s", mode)
        self._cart.clear()
        self._nav.go(AppScreen.SUCCESS)
        sec = random.randint(
            self._settings.success.auto_return_min_sec,
            self._settings.success.auto_return_max_sec,
        )
        for remaining in range(sec, 0, -1):
            # schedule countdown labels
            pass
        success_scr = self._screens[AppScreen.SUCCESS]
        assert isinstance(success_scr, SuccessScreen)

        def tick(left: int = sec) -> None:
            if left <= 0:
                self._full_reset()
                return
            success_scr.set_countdown_text(f"Возврат в меню через {left} сек…")
            QTimer.singleShot(1000, lambda: tick(left - 1))

        tick()

    def _payment_failed(self) -> None:
        sbp_scr = self._screens.get(AppScreen.PAYMENT_SBP)
        if isinstance(sbp_scr, PaymentSbpScreen):
            sbp_scr.stop()
        self._nav.go(AppScreen.PAYMENT_ERROR)

    def _on_offline(self, offline: bool) -> None:
        if offline and self._nav.current in (
            AppScreen.PAYMENT_METHOD,
            AppScreen.PAYMENT_SBP,
            AppScreen.PAYMENT_CARD,
        ):
            self._nav.go(AppScreen.OFFLINE)

    def _confirm_restart(self) -> None:
        if self._cart.positions_count == 0:
            self._full_reset()
            return
        box = QMessageBox(self)
        box.setWindowTitle("Сброс")
        box.setText("Очистить корзину и начать заново?")
        box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        box.button(QMessageBox.StandardButton.Yes).setText("Да")
        box.button(QMessageBox.StandardButton.No).setText("Нет")
        if box.exec() == QMessageBox.StandardButton.Yes:
            self._full_reset()

    def _full_reset(self) -> None:
        self._cart.clear()
        self._idle_overlay.hide()
        sbp_scr = self._screens.get(AppScreen.PAYMENT_SBP)
        if isinstance(sbp_scr, PaymentSbpScreen):
            sbp_scr.stop()
        card_scr = self._screens.get(AppScreen.PAYMENT_CARD)
        if isinstance(card_scr, PaymentCardScreen):
            card_scr.stop()
        self._nav.reset_to_start()
        self._idle.bump()

    def _on_idle_reset(self) -> None:
        self._idle_overlay.hide()
        self._full_reset()

    def eventFilter(self, obj, event) -> bool:
        if event.type() in (
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseButtonRelease,
            QEvent.Type.TouchBegin,
            QEvent.Type.KeyPress,
        ):
            self._idle.bump()
        return super().eventFilter(obj, event)

    def closeEvent(self, event) -> None:
        if self._keyboard:
            self._keyboard.uninstall()
        super().closeEvent(event)
