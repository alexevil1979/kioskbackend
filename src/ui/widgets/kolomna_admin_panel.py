from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QRectF
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.core.config import Settings
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_cta import cta_swatch_check_color, normalize_cta_color
from src.ui.kolomna_prefs import KolomnaPrefs, save_kolomna_prefs
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, INK_30, INK_60, KolomnaMetrics, scale
from src.ui.kolomna_runtime_mode import integration_label
from src.ui.scroll_utils import enable_kinetic_scroll


def _card_shadow(widget: QWidget, metrics: KolomnaMetrics) -> None:
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(scale(60, metrics.width))
    shadow.setOffset(0, scale(24, metrics.width))
    shadow.setColor(QColor(20, 56, 33, 102))
    widget.setGraphicsEffect(shadow)



def _paint_card_shadow(p: QPainter, card_rect: QRectF, radius: float, metrics: KolomnaMetrics) -> None:
    """box-shadow: 0 24px 60px -24px rgba(20,56,33,.4)."""
    w = metrics.width
    shrink = scale(24, w)
    for y_off, alpha in (
        (scale(18, w), 14),
        (scale(24, w), 28),
        (scale(30, w), 16),
    ):
        sr = QRectF(
            shrink / 2,
            y_off,
            card_rect.width() - shrink,
            card_rect.height() - shrink / 2,
        )
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(20, 56, 33, alpha))
        p.drawRoundedRect(sr, radius, radius)


class _RoundedCardShell(QWidget):
    """Скруглённая карточка + мягкая тень (paintEvent, без артефактов Qt)."""

    def __init__(
        self,
        card: QFrame,
        metrics: KolomnaMetrics,
        *,
        border: int = 0,
        border_color: str | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._m = metrics
        self._r = metrics.radius
        self._border = border
        self._border_color = QColor(border_color) if border_color else None
        card.setGraphicsEffect(None)
        card.setParent(self)
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card.setStyleSheet("QFrame { background: transparent; border: none; }")
        self._card = card
        self.setStyleSheet("background: transparent;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def _card_height(self) -> int:
        return max(self._card.minimumHeight(), self._card.sizeHint().height())

    def _shadow_bleed(self) -> int:
        return scale(20, self._m.width)

    def _sync_geometry(self) -> None:
        w = max(1, self.width())
        h = self._card_height()
        self._card.setGeometry(0, 0, w, h)
        self.setFixedHeight(h + self._shadow_bleed())

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = max(1, self.width())
        h = self._card_height()
        r = float(self._r)
        card_rect = QRectF(0, 0, w, h)

        _paint_card_shadow(p, card_rect, r, self._m)

        p.setBrush(QColor("#FFFFFF"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(card_rect, r, r)
        if self._border > 0 and self._border_color is not None:
            pen = QPen(self._border_color)
            pen.setWidth(self._border)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            inset = self._border / 2
            p.drawRoundedRect(
                QRectF(inset, inset, w - self._border, h - self._border),
                r,
                r,
            )
        p.end()
        super().paintEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._sync_geometry()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._sync_geometry()

    def sizeHint(self):  # noqa: ANN201
        h = self._card_height()
        return QSize(0, h + self._shadow_bleed())


def _wrap_rounded_card(
    card: QFrame,
    metrics: KolomnaMetrics,
    *,
    border: int = 0,
    border_color: str | None = None,
) -> QWidget:
    return _RoundedCardShell(card, metrics, border=border, border_color=border_color)


def _blend_on_cream(fg_hex: str, alpha: float) -> str:
    """Цвет как opacity поверх CREAM (для preview-bar без Qt opacity)."""
    fg = QColor(fg_hex)
    bg = QColor(CREAM)
    r = round(alpha * fg.red() + (1 - alpha) * bg.red())
    g = round(alpha * fg.green() + (1 - alpha) * bg.green())
    b = round(alpha * fg.blue() + (1 - alpha) * bg.blue())
    return f"#{r:02X}{g:02X}{b:02X}"


class _SwitchIndicator(QFrame):
    def __init__(self, on: bool, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        w = metrics.width
        self._pad = scale(6, w)
        self._travel = scale(60, w)
        sw_w = scale(132, w)
        sw_h = scale(72, w)
        knob = scale(60, w)
        self.setFixedSize(sw_w, sw_h)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._knob = QFrame(self)
        self._knob.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._knob.setFixedSize(knob, knob)
        kr = knob // 2
        self._knob.setStyleSheet(
            f"QFrame {{ background: #FFFFFF; border-radius: {kr}px; border: none; }}"
        )
        knob_shadow = QGraphicsDropShadowEffect(self._knob)
        knob_shadow.setBlurRadius(scale(12, w))
        knob_shadow.setOffset(0, scale(4, w))
        knob_shadow.setColor(QColor(0, 0, 0, 56))
        self._knob.setGraphicsEffect(knob_shadow)
        self.set_on(on)

    def set_on(self, on: bool) -> None:
        bg = GREEN if on else INK_30
        r = self.height() // 2
        self.setStyleSheet(f"QFrame {{ background: {bg}; border-radius: {r}px; border: none; }}")
        self._knob.move(self._pad + (self._travel if on else 0), self._pad)


class _ToggleTitle(QWidget):
    """admin-choice__title — рисуем сами, чтобы текст не обрезался Qt-ом."""

    def __init__(self, title: str, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._title = title
        self._m = metrics
        self._base_fs = scale(34, metrics.width)
        self._min_fs = scale(24, metrics.width)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(0)

    def _pick_font(self, avail: int) -> QFont:
        for fs in range(self._base_fs, self._min_fs - 1, -1):
            font = kolomna_font(fs, QFont.Weight.ExtraBold)
            fm = QFontMetrics(font)
            if fm.horizontalAdvance(self._title) <= avail:
                return font
        return kolomna_font(self._min_fs, QFont.Weight.ExtraBold)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        font = self._pick_font(max(1, self.width()))
        p.setFont(font)
        p.setPen(QColor(GREEN))
        rect = self.rect()
        if QFontMetrics(font).horizontalAdvance(self._title) <= max(1, self.width()):
            p.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._title)
        else:
            p.drawText(
                rect,
                Qt.AlignmentFlag.AlignLeft
                | Qt.AlignmentFlag.AlignVCenter
                | Qt.TextFlag.TextWordWrap,
                self._title,
            )
        p.end()

    def set_title(self, title: str) -> None:
        self._title = title
        self.update()


class _AdminToggleRow(QFrame):
    def __init__(self, title: str, on: bool, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._on = on
        self._title = title
        self._pad = scale(32, metrics.width)
        self._gap = scale(28, metrics.width)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumHeight(scale(136, metrics.width))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(self._pad, self._pad, self._pad, self._pad)
        lay.setSpacing(self._gap)

        self._txt = _ToggleTitle(title, metrics)
        lay.addWidget(self._txt, stretch=1)

        self._switch = _SwitchIndicator(on, metrics)
        lay.addWidget(self._switch, alignment=Qt.AlignmentFlag.AlignVCenter)
        self._apply_style()

    def _apply_style(self) -> None:
        self.setStyleSheet("QFrame { background: transparent; border: none; }")

    def is_on(self) -> bool:
        return self._on

    def set_on(self, on: bool) -> None:
        self._on = on
        self._switch.set_on(on)

    def set_title(self, title: str) -> None:
        self._title = title
        self._txt.set_title(title)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_on(not self._on)
        super().mouseReleaseEvent(event)


class _LayoutPreview(QFrame):
    def __init__(self, mode: str, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        w = metrics.width
        self.setFixedHeight(scale(150, w))
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"QFrame {{ background: {CREAM}; border-radius: {scale(16, w)}px; border: none; }}"
        )
        pad = scale(18, w)
        if mode == "list":
            lay = QVBoxLayout(self)
            lay.setContentsMargins(pad, pad, pad, pad)
            lay.setSpacing(scale(12, w))
            self._bars: list[QFrame] = []
            for _ in range(3):
                bar = QFrame()
                bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
                bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self._bars.append(bar)
                lay.addWidget(bar, stretch=1)
        else:
            lay = QGridLayout(self)
            lay.setContentsMargins(pad, pad, pad, pad)
            lay.setSpacing(scale(12, w))
            self._cells: list[QFrame] = []
            for i in range(4):
                cell = QFrame()
                cell.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
                self._cells.append(cell)
                lay.addWidget(cell, i // 2, i % 2)
        self.set_active(False)

    def set_active(self, active: bool) -> None:
        w = self._m.width
        bg = _blend_on_cream(GREEN, 0.82) if active else CREAM_DEEP
        style = (
            f"QFrame {{ background: {bg}; border-radius: {scale(8, w)}px; border: none; }}"
        )
        items = getattr(self, "_bars", None) or getattr(self, "_cells", [])
        for item in items:
            item.setStyleSheet(style)


class _RadioIndicator(QFrame):
    """admin-choice__radio: кольцо off; on — зелёный диск + inset 8px белое кольцо."""

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        w = metrics.width
        rs = scale(48, w)
        self._border = scale(5, w)
        inset = scale(8, w)
        self.setFixedSize(rs, rs)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        white_d = rs - 2 * self._border
        self._white = QFrame(self)
        self._white.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._white.setFixedSize(white_d, white_d)
        self._white.move(self._border, self._border)
        wr = white_d // 2
        self._white.setStyleSheet(
            f"QFrame {{ background: #FFFFFF; border-radius: {wr}px; border: none; }}"
        )

        center_d = max(4, white_d - 2 * inset)
        self._center = QFrame(self)
        self._center.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._center.setFixedSize(center_d, center_d)
        self._center.move(self._border + inset, self._border + inset)
        cr = center_d // 2
        self._center.setStyleSheet(
            f"QFrame {{ background: {GREEN}; border-radius: {cr}px; border: none; }}"
        )
        self.set_active(False)

    def set_active(self, active: bool) -> None:
        r = self.width() // 2
        b = self._border
        if active:
            self.setStyleSheet(
                f"QFrame {{ background: {GREEN}; border: {b}px solid {GREEN}; "
                f"border-radius: {r}px; }}"
            )
            self._white.show()
            self._center.show()
        else:
            self.setStyleSheet(
                f"QFrame {{ background: transparent; border: {b}px solid {INK_30}; "
                f"border-radius: {r}px; }}"
            )
            self._white.hide()
            self._center.hide()


class _AdminLayoutChoice(QFrame):
    clicked = pyqtSignal()

    def __init__(
        self,
        mode: str,
        title: str,
        desc: str,
        active: bool,
        metrics: KolomnaMetrics,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._mode = mode
        self._m = metrics
        self._active = active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(0)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(scale(32, metrics.width), scale(32, metrics.width), scale(32, metrics.width), scale(32, metrics.width))
        lay.setSpacing(scale(22, metrics.width))
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._preview = _LayoutPreview(mode, metrics)
        lay.addWidget(self._preview)

        text_block = QWidget()
        text_block.setStyleSheet("background: transparent; border: none;")
        text_lay = QVBoxLayout(text_block)
        text_lay.setContentsMargins(0, 0, 0, 0)
        text_lay.setSpacing(scale(6, metrics.width))

        t = QLabel(title)
        t.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.ExtraBold))
        t.setStyleSheet(f"color: {GREEN}; background: transparent; border: none; font-weight: 800;")
        t.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        text_lay.addWidget(t)

        d = QLabel(desc)
        d.setWordWrap(True)
        d.setFont(kolomna_font(metrics.fs_label, QFont.Weight.DemiBold))
        d.setStyleSheet(f"color: {INK_60}; background: transparent; border: none; font-weight: 600;")
        d.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        text_lay.addWidget(d)
        lay.addWidget(text_block)

        self._radio = _RadioIndicator(metrics)
        lay.addWidget(self._radio)

        self.set_active(active)

    def set_active(self, active: bool) -> None:
        self._active = active
        w = self._m.width
        r = self._m.radius
        border = f"4px solid {GREEN}" if active else "4px solid transparent"
        self.setStyleSheet(
            f"QFrame {{ background: transparent; border: {border}; border-radius: {r}px; }}"
        )
        self._preview.set_active(active)
        self._radio.set_active(active)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class _SwatchChip(QWidget):
    """Цветной квадрат с нарисованной галочкой (не зависит от глифа шрифта)."""

    def __init__(self, code: str, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._code = code
        self._m = metrics
        self._active = False
        chip_sz = scale(132, metrics.width)
        self._chip_r = scale(26, metrics.width)
        self.setFixedSize(chip_sz, chip_sz)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def set_active(self, active: bool) -> None:
        self._active = active
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        r = float(self._chip_r)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self._code))
        p.drawRoundedRect(rect, r, r)
        if self._active:
            stroke = max(3, scale(6, self._m.width))
            pen = QPen(QColor(cta_swatch_check_color(self._code)), stroke)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            cx, cy = rect.center().x(), rect.center().y()
            size = min(rect.width(), rect.height()) * 0.34
            path = QPainterPath()
            path.moveTo(cx - size * 0.42, cy + size * 0.02)
            path.lineTo(cx - size * 0.06, cy + size * 0.36)
            path.lineTo(cx + size * 0.46, cy - size * 0.34)
            p.drawPath(path)
        p.end()


class _SwatchStack(QFrame):
    """admin-swatch__chip + кольца выбора (без тени у невыбранных)."""

    def __init__(self, chip: QWidget, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._chip = chip
        self._m = metrics
        w = metrics.width
        self._chip_sz = scale(132, w)
        self._ring_outer = scale(12, w)
        self._ring_cream = scale(6, w)
        self._chip_r = scale(26, w)
        stack = self._chip_sz + 2 * self._ring_outer
        self.setFixedSize(stack, stack)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        chip.setParent(self)
        chip.move(self._ring_outer, self._ring_outer)
        self._active = False

    def set_active(self, active: bool) -> None:
        self._active = active
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self.width() / 2
        cy = self.height() / 2
        half = self._chip_sz / 2

        if self._active:
            for extra, color in (
                (self._ring_outer, QColor(GREEN)),
                (self._ring_cream, QColor(CREAM)),
            ):
                side = (half + extra) * 2
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(color)
                p.drawRoundedRect(
                    QRectF(cx - side / 2, cy - side / 2, side, side),
                    self._chip_r + extra,
                    self._chip_r + extra,
                )
        p.end()
        super().paintEvent(event)


class _ColorSwatch(QFrame):
    clicked = pyqtSignal()

    def __init__(self, code: str, name: str, active: bool, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._code = code
        self._m = metrics
        self._active = active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        w = metrics.width
        chip_sz = scale(132, w)
        ring_outer = scale(12, w)
        stack_sz = chip_sz + 2 * ring_outer

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(scale(14, w))
        lay.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._chip = _SwatchChip(code, metrics)
        self._stack = _SwatchStack(self._chip, metrics)
        lay.addWidget(self._stack, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._name = QLabel(name)
        self._name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name.setFont(kolomna_font(metrics.fs_label, QFont.Weight.ExtraBold))
        self._name.setStyleSheet(f"color: {GREEN}; background: transparent; font-weight: 800;")
        lay.addWidget(self._name)

        self.setFixedWidth(stack_sz)
        self.setStyleSheet("QFrame { background: transparent; border: none; }")
        self.set_active(active)

    def set_active(self, active: bool) -> None:
        self._active = active
        self._chip.set_active(active)
        self._stack.set_active(active)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class KolomnaAdminPanel(QWidget):
    prefs_changed = pyqtSignal(KolomnaPrefs)
    quit_requested = pyqtSignal()

    def __init__(
        self,
        metrics: KolomnaMetrics,
        prefs: KolomnaPrefs,
        *,
        settings: Settings | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._m = metrics
        self._settings = settings
        self._prefs = KolomnaPrefs(
            show_attract=prefs.show_attract,
            menu_layout=prefs.menu_layout,
            cta_color=prefs.cta_color,
            skip_product=prefs.skip_product,
            load_api_images=prefs.load_api_images,
            breathe_button_text=prefs.breathe_button_text,
            payment_sbp_enabled=prefs.payment_sbp_enabled,
            payment_card_enabled=prefs.payment_card_enabled,
            hours=prefs.hours,
            lang=prefs.lang,
            api_mode=prefs.api_mode,
        )
        self.setVisible(False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: rgba(20, 56, 33, 0.6);")

        pad_outer = scale(70, metrics.width)
        avail_w = max(1, metrics.width - 2 * pad_outer)
        box_w = min(scale(880, metrics.width), avail_w)
        pad64 = scale(64, metrics.width)
        sec_gap = scale(40, metrics.width)
        max_h = metrics.height - 2 * pad_outer

        outer = QVBoxLayout(self)
        outer.setContentsMargins(pad_outer, pad_outer, pad_outer, pad_outer)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._box = QWidget()
        self._box.setObjectName("KolomnaAdminPanelBox")
        self._box.setFixedWidth(box_w)
        self._box.setFixedHeight(max_h)
        self._box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._box.setStyleSheet(
            f"QWidget#KolomnaAdminPanelBox {{ background: {CREAM}; "
            f"border-radius: {metrics.radius_lg}px; }}"
        )
        _card_shadow(self._box, metrics)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(False)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        enable_kinetic_scroll(self._scroll)

        self._inner = QWidget()
        self._inner.setStyleSheet("background: transparent;")
        self._inner.setMinimumWidth(box_w)
        self._inner.setMaximumWidth(box_w)
        bl = QVBoxLayout(self._inner)
        bl.setContentsMargins(pad64, pad64, pad64, pad64 + scale(40, metrics.width))
        bl.setSpacing(sec_gap)

        eyebrow = QLabel(S.ADMIN_ACCESS.upper())
        eyebrow.setFont(kolomna_font(metrics.fs_label, QFont.Weight.ExtraBold))
        eyebrow.setStyleSheet(
            f"color: {GREEN}; background: transparent; font-weight: 800; letter-spacing: 0.14em;"
        )
        title = QLabel(S.ADMIN_TITLE)
        title.setWordWrap(True)
        title.setFont(kolomna_font(metrics.fs_h1, QFont.Weight.Black))
        title.setStyleSheet(
            f"color: {GREEN}; background: transparent; font-weight: 900; "
            f"font-size: {metrics.fs_h1}px; letter-spacing: -0.02em;"
        )
        head = QWidget()
        head_lay = QVBoxLayout(head)
        head_lay.setContentsMargins(0, 0, 0, 0)
        head_lay.setSpacing(scale(8, metrics.width))
        head_lay.addWidget(eyebrow)
        head_lay.addWidget(title)
        bl.addWidget(head)

        if settings is not None:
            runtime_wrap = QWidget()
            runtime_wrap.setStyleSheet("background: transparent;")
            runtime_lay = QVBoxLayout(runtime_wrap)
            runtime_lay.setContentsMargins(0, 0, 0, 0)
            runtime_lay.setSpacing(scale(16, metrics.width))
            self._api_toggle = _AdminToggleRow(
                S.ADMIN_API_MODE_TOGGLE, self._prefs.api_mode, metrics
            )
            runtime_lay.addWidget(self._api_toggle)
            self._integration_lbl = QLabel(
                f"{S.ADMIN_RUNTIME_INTEGRATION}: {integration_label(settings.hardware.integration_mode)}"
            )
            self._integration_lbl.setWordWrap(True)
            self._integration_lbl.setFont(kolomna_font(metrics.fs_label, QFont.Weight.Medium))
            self._integration_lbl.setStyleSheet(f"color: {INK_60}; background: transparent; padding: 0 {scale(32, metrics.width)}px;")
            runtime_lay.addWidget(self._integration_lbl)
            bl.addWidget(
                self._admin_sec(
                    metrics,
                    S.ADMIN_RUNTIME_SECTION,
                    S.ADMIN_RUNTIME_HINT,
                    _wrap_rounded_card(
                        runtime_wrap,
                        metrics,
                        border=scale(4, metrics.width),
                        border_color=CREAM_DEEP,
                    ),
                )
            )
        else:
            self._api_toggle = None
            self._integration_lbl = None

        self._start_toggle = _AdminToggleRow(S.ADMIN_START_TOGGLE, self._prefs.show_attract, metrics)
        bl.addWidget(
            self._admin_sec(
                metrics,
                S.ADMIN_START_SECTION,
                S.ADMIN_START_HINT,
                _wrap_rounded_card(self._start_toggle, metrics),
            )
        )

        self._skip_toggle = _AdminToggleRow(S.ADMIN_SKIP_TOGGLE, self._prefs.skip_product, metrics)
        bl.addWidget(
            self._admin_sec(
                metrics,
                S.ADMIN_SKIP_SECTION,
                S.ADMIN_SKIP_HINT,
                _wrap_rounded_card(self._skip_toggle, metrics),
            )
        )

        self._images_toggle = _AdminToggleRow(
            S.ADMIN_IMAGES_TOGGLE, self._prefs.load_api_images, metrics
        )
        bl.addWidget(
            self._admin_sec(
                metrics,
                S.ADMIN_IMAGES_SECTION,
                S.ADMIN_IMAGES_HINT,
                _wrap_rounded_card(self._images_toggle, metrics),
            )
        )

        self._breathe_toggle = _AdminToggleRow(
            S.ADMIN_BREATHE_TOGGLE, self._prefs.breathe_button_text, metrics
        )
        bl.addWidget(
            self._admin_sec(
                metrics,
                S.ADMIN_BREATHE_SECTION,
                S.ADMIN_BREATHE_HINT,
                _wrap_rounded_card(self._breathe_toggle, metrics),
            )
        )

        pay_wrap = QWidget()
        pay_wrap.setStyleSheet("background: transparent;")
        pay_lay = QVBoxLayout(pay_wrap)
        pay_lay.setContentsMargins(0, 0, 0, 0)
        pay_lay.setSpacing(scale(20, metrics.width))
        self._pay_sbp_toggle = _AdminToggleRow(
            S.ADMIN_PAY_SBP_TOGGLE, self._prefs.payment_sbp_enabled, metrics
        )
        self._pay_card_toggle = _AdminToggleRow(
            S.ADMIN_PAY_CARD_TOGGLE, self._prefs.payment_card_enabled, metrics
        )
        pay_lay.addWidget(self._pay_sbp_toggle)
        pay_lay.addWidget(self._pay_card_toggle)
        bl.addWidget(
            self._admin_sec(
                metrics,
                S.ADMIN_PAY_SECTION,
                S.ADMIN_PAY_HINT,
                _wrap_rounded_card(pay_wrap, metrics),
            )
        )

        hours_h = scale(88, metrics.width)
        pad_h = scale(32, metrics.width)
        pad_v = scale(28, metrics.width)
        hours_wrap = QFrame()
        hours_wrap.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        hours_wrap.setMinimumHeight(hours_h)
        hours_wrap.setStyleSheet("QFrame { background: transparent; border: none; }")
        hours_lay = QHBoxLayout(hours_wrap)
        hours_lay.setContentsMargins(pad_h, pad_v, pad_h, pad_v)
        self._hours_edit = QLineEdit(self._prefs.hours)
        self._hours_edit.setFrame(False)
        self._hours_edit.setMinimumHeight(scale(32, metrics.width))
        self._hours_edit.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self._hours_edit.setFont(kolomna_font(metrics.fs_body, QFont.Weight.Bold))
        self._hours_edit.setStyleSheet(
            f"QLineEdit {{ background: transparent; border: none; color: {GREEN}; "
            f"font-weight: 700; font-size: {metrics.fs_body}px; padding: 0; margin: 0; }}"
        )
        hours_lay.addWidget(self._hours_edit)
        bl.addWidget(
            self._admin_sec(
                metrics,
                S.ADMIN_HOURS_SECTION,
                S.ADMIN_HOURS_HINT,
                _wrap_rounded_card(
                    hours_wrap,
                    metrics,
                    border=scale(4, metrics.width),
                    border_color=CREAM_DEEP,
                ),
            )
        )

        sw_row = QWidget()
        sw_lay = QHBoxLayout(sw_row)
        sw_lay.setContentsMargins(0, 0, 0, 0)
        sw_lay.setSpacing(scale(24, metrics.width))
        self._color_swatches: dict[str, _ColorSwatch] = {}
        for code, name in (
            ("#1F4D2A", S.ADMIN_COLOR_GREEN),
            ("#D9143A", S.ADMIN_COLOR_STRAWBERRY),
            ("#F4C90A", S.ADMIN_COLOR_YELLOW),
        ):
            sw = _ColorSwatch(code, name, self._prefs.cta_color == code, metrics)
            sw.clicked.connect(lambda c=code: self._set_color(c))
            self._color_swatches[code] = sw
            sw_lay.addWidget(sw)
        sw_lay.addStretch(1)
        bl.addWidget(self._admin_sec(metrics, S.ADMIN_COLOR_SECTION, S.ADMIN_COLOR_HINT, sw_row))

        layout_row = QWidget()
        layout_row.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout_lay = QGridLayout(layout_row)
        layout_lay.setContentsMargins(0, 0, 0, 0)
        layout_lay.setSpacing(metrics.gap)
        layout_lay.setColumnStretch(0, 1)
        layout_lay.setColumnStretch(1, 1)
        layout_lay.setColumnMinimumWidth(0, 0)
        layout_lay.setColumnMinimumWidth(1, 0)
        self._layout_choices: dict[str, _AdminLayoutChoice] = {}
        for col, (mode, t, d) in enumerate(
            (
                ("list", S.ADMIN_LAYOUT_LIST, S.ADMIN_LAYOUT_LIST_DESC),
                ("grid", S.ADMIN_LAYOUT_GRID, S.ADMIN_LAYOUT_GRID_DESC),
            )
        ):
            ch = _AdminLayoutChoice(mode, t, d, self._prefs.menu_layout == mode, metrics)
            ch.clicked.connect(lambda m=mode: self._set_layout(m))
            self._layout_choices[mode] = ch
            layout_lay.addWidget(_wrap_rounded_card(ch, metrics), 0, col)
        bl.addWidget(self._admin_sec(metrics, S.ADMIN_LAYOUT_SECTION, S.ADMIN_LAYOUT_HINT, layout_row))

        done_h = scale(104, metrics.width)
        done_r = done_h // 2
        done = QPushButton(S.ADMIN_DONE)
        done.setObjectName("KolomnaAdminDone")
        done.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        done.setCursor(Qt.CursorShape.PointingHandCursor)
        done.setFixedHeight(done_h)
        done.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        done.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.ExtraBold))
        done.setStyleSheet(
            f"QPushButton#KolomnaAdminDone {{ background: {GREEN}; color: {CREAM}; border: none; "
            f"border-radius: {done_r}px; font-weight: 800; font-size: {metrics.fs_h3}px; "
            f"padding: {scale(28, metrics.width)}px {scale(56, metrics.width)}px; "
            f"min-height: {done_h}px; max-height: {done_h}px; }}"
            f"QPushButton#KolomnaAdminDone:pressed {{ background: {GREEN}; opacity: 0.92; }}"
        )
        done.clicked.connect(self._save)
        bl.addWidget(done)

        quit_h = scale(104, metrics.width)
        quit_r = quit_h // 2
        quit_border = max(2, scale(3, metrics.width))
        self._quit_btn = QPushButton(S.ADMIN_QUIT_APP)
        self._quit_btn.setObjectName("KolomnaAdminQuit")
        self._quit_btn.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._quit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._quit_btn.setFixedHeight(quit_h)
        self._quit_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._quit_btn.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.ExtraBold))
        self._quit_btn.setStyleSheet(
            f"QPushButton#KolomnaAdminQuit {{ background: transparent; color: {GREEN}; "
            f"border: {quit_border}px solid {GREEN}; border-radius: {quit_r}px; "
            f"font-weight: 800; font-size: {metrics.fs_h3}px; "
            f"padding: {scale(28, metrics.width)}px {scale(56, metrics.width)}px; "
            f"min-height: {quit_h}px; max-height: {quit_h}px; }}"
            f"QPushButton#KolomnaAdminQuit:pressed {{ background: {GREEN}; color: {CREAM}; }}"
        )
        self._quit_btn.clicked.connect(self.quit_requested.emit)
        bl.addWidget(self._quit_btn)

        self._scroll.setWidget(self._inner)
        self._finalize_inner_size()

        box_lay = QVBoxLayout(self._box)
        box_lay.setContentsMargins(0, 0, 0, 0)
        box_lay.addWidget(self._scroll)

        outer.addWidget(self._box, alignment=Qt.AlignmentFlag.AlignCenter)

    def _finalize_inner_size(self) -> None:
        lay = self._inner.layout()
        if lay is None:
            return
        lay.activate()
        w = self._inner.maximumWidth()
        h = lay.sizeHint().height()
        self._inner.setFixedSize(w, h)

    @staticmethod
    def _admin_sec(metrics: KolomnaMetrics, section: str, hint: str, body: QWidget) -> QWidget:
        host = QWidget()
        host.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(host)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(scale(26, metrics.width))

        top = QWidget()
        top_lay = QVBoxLayout(top)
        top_lay.setContentsMargins(0, 0, 0, 0)
        top_lay.setSpacing(scale(6, metrics.width))
        lbl = QLabel(section)
        lbl.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.ExtraBold))
        lbl.setStyleSheet(f"color: {GREEN}; background: transparent; font-weight: 800;")
        h = QLabel(hint)
        h.setWordWrap(True)
        h.setFont(kolomna_font(metrics.fs_lead, QFont.Weight.Medium))
        h.setStyleSheet(f"color: {INK_60}; background: transparent; font-weight: 500;")
        top_lay.addWidget(lbl)
        top_lay.addWidget(h)
        lay.addWidget(top)
        lay.addWidget(body)
        return host

    def _set_color(self, code: str) -> None:
        self._prefs.cta_color = normalize_cta_color(code)
        chosen = self._prefs.cta_color
        for c, sw in self._color_swatches.items():
            sw.set_active(normalize_cta_color(c) == chosen)

    def _set_layout(self, mode: str) -> None:
        self._prefs.menu_layout = mode
        for m, ch in self._layout_choices.items():
            ch.set_active(m == mode)

    def retranslate(self) -> None:
        self._quit_btn.setText(S.ADMIN_QUIT_APP)
        self._images_toggle.set_title(S.ADMIN_IMAGES_TOGGLE)
        self._breathe_toggle.set_title(S.ADMIN_BREATHE_TOGGLE)
        self._pay_sbp_toggle.set_title(S.ADMIN_PAY_SBP_TOGGLE)
        self._pay_card_toggle.set_title(S.ADMIN_PAY_CARD_TOGGLE)
        if self._api_toggle is not None:
            self._api_toggle.set_title(S.ADMIN_API_MODE_TOGGLE)
        if self._integration_lbl is not None and self._settings is not None:
            self._integration_lbl.setText(
                f"{S.ADMIN_RUNTIME_INTEGRATION}: "
                f"{integration_label(self._settings.hardware.integration_mode)}"
            )

    def _save(self) -> None:
        self._prefs.show_attract = self._start_toggle.is_on()
        self._prefs.skip_product = self._skip_toggle.is_on()
        self._prefs.load_api_images = self._images_toggle.is_on()
        self._prefs.breathe_button_text = self._breathe_toggle.is_on()
        self._prefs.payment_sbp_enabled = self._pay_sbp_toggle.is_on()
        self._prefs.payment_card_enabled = self._pay_card_toggle.is_on()
        if self._api_toggle is not None:
            self._prefs.api_mode = self._api_toggle.is_on()
        from src.ui.kolomna_prefs import normalize_payment_methods

        normalize_payment_methods(self._prefs)
        self._prefs.hours = self._hours_edit.text().strip() or self._prefs.hours
        save_kolomna_prefs(self._prefs)
        self.prefs_changed.emit(self._prefs)
        self.hide()

    def scroll_to(self, where: str = "top") -> None:
        bar = self._scroll.verticalScrollBar()
        bar.setValue(bar.maximum() if where == "bottom" else 0)

    def show_modal(self, scroll: str = "top") -> None:
        if self._api_toggle is not None:
            self._api_toggle.set_on(self._prefs.api_mode)
        if self._integration_lbl is not None and self._settings is not None:
            self._integration_lbl.setText(
                f"{S.ADMIN_RUNTIME_INTEGRATION}: "
                f"{integration_label(self._settings.hardware.integration_mode)}"
            )
        self._start_toggle.set_on(self._prefs.show_attract)
        self._skip_toggle.set_on(self._prefs.skip_product)
        self._images_toggle.set_on(self._prefs.load_api_images)
        self._breathe_toggle.set_on(self._prefs.breathe_button_text)
        self._pay_sbp_toggle.set_on(self._prefs.payment_sbp_enabled)
        self._pay_card_toggle.set_on(self._prefs.payment_card_enabled)
        self._hours_edit.setText(self._prefs.hours)
        chosen = normalize_cta_color(self._prefs.cta_color)
        for c, sw in self._color_swatches.items():
            sw.set_active(normalize_cta_color(c) == chosen)
        for m, ch in self._layout_choices.items():
            ch.set_active(m == self._prefs.menu_layout)
        self.setGeometry(0, 0, self.parentWidget().width(), self.parentWidget().height())
        self.raise_()
        self.show()
        self._finalize_inner_size()
        self.scroll_to(scroll)
        QTimer.singleShot(80, lambda: (self._finalize_inner_size(), self.scroll_to(scroll)))

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            top_left = self._box.mapTo(self, self._box.rect().topLeft())
            box_rect = self._box.rect()
            box_rect.moveTopLeft(top_left)
            if not box_rect.contains(pos):
                self.hide()
        super().mouseReleaseEvent(event)
