from __future__ import annotations

import logging
import math

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from src.core.config import ROOT, Settings
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import fmt_price
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, INK_60, KolomnaMetrics, scale
from src.ui.qr_render import render_qr_pixmap
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.kolomna_pay_due import KolomnaPayDueRow
from src.ui.widgets.kolomna_topbar import KolomnaTopBar

logger = logging.getLogger(__name__)


class _QrGenRingSpinner(QWidget):
    """Кольцо загрузки QR: бегущая дуга по контуру."""

    def __init__(self, size: int, stroke: int, parent=None) -> None:
        super().__init__(parent)
        self._stroke = max(2, stroke)
        self._angle = 0.0
        self._phase = 0.0
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self._timer = QTimer(self)
        self._timer.setInterval(32)
        self._timer.timeout.connect(self._tick)

    def start(self) -> None:
        if not self._timer.isActive():
            self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def _tick(self) -> None:
        self._angle = (self._angle + 5.5) % 360.0
        self._phase = (self._phase + 4.0) % 360.0
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = self._stroke / 2.0 + 1.0
        rect = QRectF(inset, inset, self.width() - inset * 2, self.height() - inset * 2)

        track = QPen(QColor(CREAM_DEEP))
        track.setWidth(self._stroke)
        track.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(track)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(rect)

        span = 55.0 + 95.0 * (0.5 + 0.5 * math.sin(math.radians(self._phase)))
        arc = QPen(QColor(GREEN))
        arc.setWidth(self._stroke)
        arc.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(arc)
        start_qt = int((90.0 - self._angle) * 16.0)
        span_qt = int(-span * 16.0)
        p.drawArc(rect, start_qt, span_qt)
        p.end()


class KolomnaSbpScreen(BaseScreen):
    cancel = pyqtSignal()
    paid = pyqtSignal()
    failed = pyqtSignal()
    qr_ready = pyqtSignal()

    def __init__(self, timeout_sec: int, settings: Settings) -> None:
        super().__init__()
        self._default_timeout_sec = timeout_sec
        self._remaining = timeout_sec
        self._payment_id = ""
        w = settings.app.content_width
        h = settings.app.content_height
        self._m = KolomnaMetrics.from_viewport(w, h)

        self.setObjectName("KolomnaSbpScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {CREAM};")
        self.setFixedSize(w, h)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._top = KolomnaTopBar(self._m, show_back=True, show_lang=True)
        self._top.set_title(S.PAY_TITLE, accent=GREEN)
        self._top.back_clicked.connect(self.cancel.emit)
        self._layout.addWidget(self._top)

        self._center = QWidget()
        center_lay = QVBoxLayout(self._center)
        center_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_lay.setSpacing(scale(40, w))
        center_lay.setContentsMargins(self._m.pad, scale(24, w), self._m.pad, self._m.pad)

        self._instr = QLabel(S.PAY_SBP_SCAN)
        self._instr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._instr.setWordWrap(True)
        self._instr.setMaximumWidth(scale(720, w))
        self._instr.setFont(kolomna_font(self._m.fs_h3, QFont.Weight.ExtraBold))
        self._instr.setStyleSheet(f"color: {GREEN}; background: transparent;")

        self._spinner = _QrGenRingSpinner(scale(140, w), scale(16, w))

        self._gen_title = QLabel(S.PAY_SBP_GEN)
        self._gen_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._gen_title.setFont(kolomna_font(self._m.fs_h2, QFont.Weight.Black))
        self._gen_title.setStyleSheet(f"color: {GREEN}; background: transparent;")

        self._gen_sub = QLabel(S.PAY_SBP_GEN_SUB)
        self._gen_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._gen_sub.setFont(kolomna_font(self._m.fs_body, QFont.Weight.Medium))
        self._gen_sub.setStyleSheet(f"color: {INK_60}; background: transparent;")

        self._qr_host = QFrame()
        self._qr_outer = scale(620, w)
        self._qr_inner = scale(572, w)
        self._qr_pix_sz = max(1, round(572 * w / 1080))
        pay_path = ROOT / "assets" / "kolomna" / "qr" / f"pay_sbp_{self._qr_pix_sz}.png"
        if not pay_path.is_file():
            alt = ROOT / "assets" / "kolomna" / "qr" / f"pay_sbp_{self._qr_pix_sz + 1}.png"
            if alt.is_file():
                self._qr_pix_sz += 1
        self._qr_edge = max(0, (self._qr_outer - self._qr_inner) // 2)
        self._qr_host.setFixedSize(self._qr_outer, self._qr_outer)
        br = scale(28, w)
        self._qr_host.setStyleSheet(f"QFrame {{ background: #FFFFFF; border-radius: {br}px; }}")
        self._qr = QLabel(self._qr_host)
        self._qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._position_qr_label()

        self._due_row = KolomnaPayDueRow(self._m, sum_font_px=scale(96, w))

        center_lay.addWidget(self._instr)
        center_lay.addWidget(self._spinner, alignment=Qt.AlignmentFlag.AlignHCenter)
        center_lay.addWidget(self._gen_title)
        center_lay.addWidget(self._gen_sub)
        center_lay.addWidget(self._qr_host, alignment=Qt.AlignmentFlag.AlignHCenter)
        center_lay.addWidget(self._due_row, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._layout.addWidget(self._center, stretch=1)
        self._show_generating()

        self._countdown = QTimer(self)
        self._countdown.timeout.connect(self._tick)
        self._spin_timer = QTimer(self)
        self._spin_timer.setSingleShot(True)

    def _position_qr_label(self) -> None:
        inset = self._qr_edge + max(0, (self._qr_inner - self._qr_pix_sz) // 2)
        self._qr.setGeometry(inset, inset, self._qr_pix_sz, self._qr_pix_sz)

    def _show_generating(self) -> None:
        self._instr.hide()
        self._qr_host.hide()
        self._spinner.show()
        self._spinner.start()
        self._gen_title.show()
        self._gen_sub.show()

    def begin_payment(self, total_rub: float = 0) -> None:
        """Сразу показать экран ожидания QR (до ответа API)."""
        self.stop()
        self._payment_id = ""
        self._show_generating()
        if total_rub > 0:
            self._due_row.set_amount(f"{fmt_price(total_rub)}\u00a0{S.CUR}")
            self._due_row.show()
        else:
            self._due_row.hide()

    def _show_qr(self) -> None:
        self._spinner.stop()
        self._spinner.hide()
        self._gen_title.hide()
        self._gen_sub.hide()
        self._instr.show()
        self._qr_host.show()
        self._due_row.show()

    def start_payment(
        self,
        qr_payload: str,
        payment_id: str,
        *,
        qr_image_b64: str = "",
        timeout_sec: int | None = None,
        total_rub: float = 0,
    ) -> None:
        self._payment_id = payment_id
        self._due_row.set_amount(f"{fmt_price(total_rub)}\u00a0{S.CUR}")
        limit = timeout_sec if timeout_sec is not None else self._default_timeout_sec
        self._remaining = max(30, int(limit))
        already_loading = self._spinner.isVisible() and not self._qr_host.isVisible()
        if not already_loading:
            self._show_generating()

        def reveal() -> None:
            from src.ui.kolomna_qr_render import load_cached_qr_pixmap, scale_qr_for_display

            pix = None
            if (qr_payload or "").strip() or (qr_image_b64 or "").strip():
                pix = render_qr_pixmap(
                    payload=qr_payload,
                    image_b64=qr_image_b64,
                    size=self._qr_pix_sz,
                )
            else:
                pix = load_cached_qr_pixmap("pay", px=self._qr_pix_sz)
                if not pix.isNull() and pix.width() != self._qr_pix_sz:
                    pix = scale_qr_for_display(pix, self._qr_pix_sz)
            if pix is not None and not pix.isNull():
                self._qr.setPixmap(pix)
            else:
                self._qr.setText("QR")
                logger.error("СБП: не удалось отрисовать QR")
            self._position_qr_label()
            self._show_qr()
            self.qr_ready.emit()

        try:
            self._spin_timer.timeout.disconnect()
        except TypeError:
            pass
        self._spin_timer.timeout.connect(reveal)
        self._spin_timer.start(0 if already_loading else 800)
        self._update_timer_label()
        self._countdown.start(1000)

    def stop(self) -> None:
        self._countdown.stop()
        self._spin_timer.stop()
        self._spinner.stop()

    def _tick(self) -> None:
        self._remaining -= 1
        if self._remaining <= 0:
            self._countdown.stop()
            self.failed.emit()

    def _update_timer_label(self) -> None:
        pass

    def retranslate(self) -> None:
        self._top.set_title(S.PAY_TITLE, accent=GREEN)
        self._top.retranslate()
        self._instr.setText(S.PAY_SBP_SCAN)
        self._gen_title.setText(S.PAY_SBP_GEN)
        self._gen_sub.setText(S.PAY_SBP_GEN_SUB)
        self._due_row.set_label(f"{S.PAY_DUE}:")
        amount = self._due_row.amount_text()
        if amount:
            parts = amount.split("\u00a0")
            if parts:
                self._due_row.set_amount(f"{parts[0]}\u00a0{S.CUR}")
