from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QRegion
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.models.product import Product
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_prefs import load_kolomna_prefs
from src.ui.kolomna_product_meta import (
    fmt_price,
    product_description,
    product_pack_label,
    product_title,
    product_variant_label,
)
from src.ui.kolomna_tokens import CREAM_DEEP, GREEN, INK_60, KolomnaMetrics, YELLOW, scale
from src.ui.widgets.kolomna_berry_art import KolomnaBerryArt


def card_shadow_bleed(metrics: KolomnaMetrics) -> int:
    return 0


def _paint_card_shadow(
    p: QPainter, card_rect: QRectF, radius: float, metrics: KolomnaMetrics
) -> None:
    return


def _clamp_wrapped_text(
    text: str,
    font: QFont,
    width: int,
    *,
    max_lines: int = 2,
    line_height: float = 1.35,
) -> tuple[str, int]:
    """Не более max_lines строк; лишнее — «…» в конце последней строки."""
    text = text.strip()
    if not text or width <= 0:
        return "", 0
    fm = QFontMetrics(font)
    line_h = max(1, round(fm.height() * line_height))
    words = text.split()
    lines: list[str] = []
    idx = 0
    while idx < len(words) and len(lines) < max_lines:
        line = ""
        while idx < len(words):
            trial = f"{line} {words[idx]}".strip()
            if fm.horizontalAdvance(trial) <= width:
                line = trial
                idx += 1
            else:
                if not line:
                    line = fm.elidedText(words[idx], Qt.TextElideMode.ElideRight, width)
                    idx += 1
                break
        if line:
            lines.append(line)
    if idx < len(words) and lines:
        ell = "…"
        last = lines[-1]
        while last and fm.horizontalAdvance(f"{last}{ell}") > width:
            last = last[:-1].rstrip()
        lines[-1] = f"{last}{ell}" if last else ell
    return "\n".join(lines), line_h * max(len(lines), 1)


def kolomna_product_titles_height(
    product: Product,
    *,
    metrics: KolomnaMetrics,
    title_px: int,
    body_w: int,
    title_weight: QFont.Weight = QFont.Weight.Black,
    variant_px: int | None = None,
    max_title_lines: int = 2,
    max_variant_lines: int = 2,
) -> int:
    title_font = kolomna_font(title_px, title_weight)
    _, title_h = _clamp_wrapped_text(
        product_title(product),
        title_font,
        body_w,
        max_lines=max_title_lines,
        line_height=1.2,
    )
    total = title_h
    variant_raw = product_variant_label(product)
    if variant_raw:
        v_px = variant_px if variant_px is not None else metrics.fs_lead
        variant_font = kolomna_font(v_px, QFont.Weight.Medium)
        _, variant_h = _clamp_wrapped_text(
            variant_raw,
            variant_font,
            body_w,
            max_lines=max_variant_lines,
            line_height=1.35,
        )
        total += variant_h
    return total


def append_kolomna_product_titles(
    lay: QVBoxLayout,
    product: Product,
    *,
    metrics: KolomnaMetrics,
    title_px: int,
    body_w: int,
    title_weight: QFont.Weight = QFont.Weight.Black,
    variant_px: int | None = None,
    max_title_lines: int = 2,
    max_variant_lines: int = 2,
) -> int:
    """Заголовок карточки: name и отдельно variant_name с API."""
    title_font = kolomna_font(title_px, title_weight)
    title_text, title_h = _clamp_wrapped_text(
        product_title(product),
        title_font,
        body_w,
        max_lines=max_title_lines,
        line_height=1.2,
    )
    title = QLabel(title_text)
    title.setWordWrap(True)
    title.setMinimumWidth(0)
    title.setMaximumWidth(body_w)
    title.setFixedHeight(title_h)
    title.setFont(title_font)
    title.setStyleSheet(f"color: {GREEN}; background: transparent;")
    lay.addWidget(title)
    total_h = title_h

    variant_raw = product_variant_label(product)
    if variant_raw:
        v_px = variant_px if variant_px is not None else metrics.fs_lead
        variant_font = kolomna_font(v_px, QFont.Weight.Medium)
        variant_text, variant_h = _clamp_wrapped_text(
            variant_raw,
            variant_font,
            body_w,
            max_lines=max_variant_lines,
            line_height=1.35,
        )
        variant = QLabel(variant_text)
        variant.setWordWrap(True)
        variant.setMinimumWidth(0)
        variant.setMaximumWidth(body_w)
        variant.setFixedHeight(variant_h)
        variant.setFont(variant_font)
        variant.setStyleSheet(
            f"color: {INK_60}; background: transparent; line-height: 135%;"
        )
        lay.addWidget(variant)
        total_h += variant_h

    return total_h


class _PackChip(QWidget):
    """chip / chip--lg — cream pill (border-radius: 999px в референсе)."""

    def __init__(
        self,
        text: str,
        metrics: KolomnaMetrics,
        *,
        large: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        w = metrics.width
        fs = scale(26, w) if large else scale(22, w)
        pad_v = scale(14, w) if large else scale(10, w)
        pad_h = scale(28, w) if large else scale(22, w)
        self._chip_text = text
        self._font = kolomna_font(fs, QFont.Weight.ExtraBold)
        fm = QFontMetrics(self._font)
        self.setFixedSize(
            fm.horizontalAdvance(text) + pad_h * 2,
            fm.height() + pad_v * 2,
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        r = rect.height() / 2.0
        pill = QPainterPath()
        pill.addRoundedRect(rect, r, r)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(CREAM_DEEP))
        p.fillPath(pill, QColor(CREAM_DEEP))
        p.setFont(self._font)
        p.setPen(QColor(GREEN))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._chip_text)
        p.end()


# «+ В корзину» в prod-row: .btn.btn--yellow (tap-comfortable 88px, padding 22×44).
PROD_ADD_BTN_MIN_HEIGHT_PX = 88
PROD_ADD_BTN_PAD_V_PX = 22
PROD_ADD_BTN_PAD_H_PX = 44

# «+ В корзину» в prod-tile__foot — компактная pill в сетке.
TILE_ADD_BTN_MIN_HEIGHT_PX = 72
TILE_ADD_BTN_PAD_V_PX = 18
TILE_ADD_BTN_PAD_H_PX = 32
TILE_MEDIA_HEIGHT_PX = 340


class _TileMediaHost(QFrame):
    """prod-tile__media: фикс. высота, фото через geometry (без layout-петли 116%)."""

    def __init__(self, berry: KolomnaBerryArt, media_h: int, border_css: str, parent=None) -> None:
        super().__init__(parent)
        self._berry = berry
        berry.setParent(self)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(media_h)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(border_css)
        self.setMinimumWidth(0)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        w, h = max(1, self.width()), self.height()
        self._berry.setGeometry(0, 0, w, h)


class _TileAddBtn(QWidget):
    """btn btn--yellow в prod-tile__foot."""

    clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._pressed = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        w = metrics.width
        text = f"+ {S.ADD_SHORT}"
        self._label = text
        self._font = kolomna_font(metrics.fs_label, QFont.Weight.ExtraBold)
        pad_v = scale(TILE_ADD_BTN_PAD_V_PX, w)
        pad_h = scale(TILE_ADD_BTN_PAD_H_PX, w)
        fm = QFontMetrics(self._font)
        btn_w = fm.horizontalAdvance(text) + pad_h * 2
        self._pill_h = scale(TILE_ADD_BTN_MIN_HEIGHT_PX, w)
        self.setFixedSize(btn_w, self._pill_h)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(0.5, 0.5, self.width() - 1, self._pill_h - 1)
        r = rect.height() / 2.0
        bg = QColor("#E0B800" if self._pressed else YELLOW)
        p.setBrush(bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, r, r)
        p.setFont(self._font)
        p.setPen(QColor(GREEN))
        p.drawText(rect.toRect(), Qt.AlignmentFlag.AlignCenter, self._label)
        p.end()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.update()
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)


class _ProdAddBtn(QWidget):
    """btn btn--yellow в prod-row__foot."""

    clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._pressed = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        w = metrics.width
        text = f"+ {S.ADD_SHORT}"
        self._label = text
        self._font = kolomna_font(metrics.fs_body, QFont.Weight.ExtraBold)
        pad_v = scale(PROD_ADD_BTN_PAD_V_PX, w)
        pad_h = scale(PROD_ADD_BTN_PAD_H_PX, w)
        fm = QFontMetrics(self._font)
        btn_w = fm.horizontalAdvance(text) + pad_h * 2
        self._pill_h = scale(PROD_ADD_BTN_MIN_HEIGHT_PX, w)
        self.setFixedSize(btn_w, self._pill_h)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(0.5, 0.5, self.width() - 1, self._pill_h - 1)
        r = rect.height() / 2.0
        bg = QColor("#E0B800" if self._pressed else YELLOW)
        p.setBrush(bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, r, r)
        p.setFont(self._font)
        p.setPen(QColor(GREEN))
        text_rect = QRectF(rect)
        p.drawText(text_rect.toRect(), Qt.AlignmentFlag.AlignCenter, self._label)
        p.end()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.update()
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)


class KolomnaProdRow(QWidget):
    """prod-row: белая карточка, фото слева, текст и «+ В корзину»."""

    clicked = pyqtSignal(str)
    add_clicked = pyqtSignal(str)

    def __init__(self, product: Product, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._product = product
        self._m = metrics
        self._radius = metrics.radius
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._clip_w = 0
        self._clip_h = 0

        media_w = scale(400, metrics.width)
        # prod-row на референсе ≈ scale(400) по высоте (400×400 @ 1080)
        self._card_h = scale(400, metrics.width)
        self._media_h = self._card_h

        self._card = QFrame()
        self._card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._card.setStyleSheet("QFrame { background: transparent; border: none; }")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, self._shadow_bleed())
        outer.setSpacing(0)
        outer.addWidget(self._card)

        root = QHBoxLayout(self._card)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(scale(28, metrics.width))

        media = KolomnaBerryArt(
            product,
            media_w,
            self._media_h,
            radius=0,
            bg=CREAM_DEEP,
            ground_shadow=False,
            fit="cover",
        )
        self._media = media
        root.addWidget(media, 0, Qt.AlignmentFlag.AlignTop)

        self._body_host = QWidget()
        self._body_host.setMinimumWidth(0)
        self._body_host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._body_host.setStyleSheet("background: transparent;")
        self._body_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        body = QVBoxLayout(self._body_host)
        body.setContentsMargins(
            0,
            scale(34, metrics.width),
            scale(36, metrics.width),
            scale(30, metrics.width),
        )
        body.setSpacing(scale(14, metrics.width))

        body_w = max(
            40,
            metrics.width - 2 * metrics.gap - media_w - scale(28, metrics.width) - scale(36, metrics.width),
        )
        append_kolomna_product_titles(
            body,
            product,
            metrics=metrics,
            title_px=metrics.fs_h2,
            body_w=body_w,
            title_weight=QFont.Weight.Black,
        )

        desc_raw = product_description(product) if load_kolomna_prefs().show_product_description else ""
        if desc_raw:
            desc_font = kolomna_font(metrics.fs_lead, QFont.Weight.Medium)
            desc_text, desc_h = _clamp_wrapped_text(desc_raw, desc_font, body_w, max_lines=2)
            d = QLabel(desc_text)
            d.setWordWrap(True)
            d.setMinimumWidth(0)
            d.setFixedHeight(desc_h)
            d.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            d.setFont(desc_font)
            d.setStyleSheet(f"color: {INK_60}; background: transparent; line-height: 135%;")
            body.addWidget(d)

        meta = QHBoxLayout()
        meta.setSpacing(scale(18, metrics.width))
        chip = _PackChip(product_pack_label(product), metrics)
        meta.addWidget(chip, alignment=Qt.AlignmentFlag.AlignVCenter)
        meta.addStretch(1)
        body.addLayout(meta)

        body.addStretch(1)

        foot = QHBoxLayout()
        foot.setSpacing(scale(20, metrics.width))
        price = QLabel(f"{fmt_price(product.price_rub)}\u00a0{S.CUR}")
        price.setFont(kolomna_font(metrics.fs_h2, QFont.Weight.Black))
        price.setStyleSheet(f"color: {GREEN}; background: transparent;")
        foot.addWidget(price, alignment=Qt.AlignmentFlag.AlignVCenter)

        foot.addStretch(1)

        add = _ProdAddBtn(metrics)
        add.clicked.connect(self._on_add)
        self._add_btn = add
        foot.addWidget(add, alignment=Qt.AlignmentFlag.AlignVCenter)

        foot_wrap = QWidget()
        foot_wrap.setStyleSheet("background: transparent;")
        foot_outer = QVBoxLayout(foot_wrap)
        foot_outer.setContentsMargins(0, scale(16, metrics.width), 0, 0)
        foot_outer.addLayout(foot)
        body.addWidget(foot_wrap)

        root.addWidget(self._body_host, stretch=1)

        self._body_host.adjustSize()
        self._card_h = max(self._card_h, self._body_host.sizeHint().height())
        self._sync_heights()

    def _sync_heights(self) -> None:
        self._media.setFixedSize(scale(400, self._m.width), self._card_h)
        self._card.setFixedHeight(self._card_h)
        total = self._card_h + self._shadow_bleed()
        self.setFixedHeight(total)

    def _shadow_bleed(self) -> int:
        return card_shadow_bleed(self._m)

    def _apply_round_clip(self) -> None:
        w = max(1, self._card.width())
        h = max(1, self._card.height())
        if w == self._clip_w and h == self._clip_h:
            return
        self._clip_w, self._clip_h = w, h
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), self._radius, self._radius)
        self._card.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = max(1, self.width())
        h = self._card_h
        r = float(self._radius)
        card_rect = QRectF(0, 0, w, h)
        _paint_card_shadow(p, card_rect, r, self._m)
        p.setBrush(QColor("#FFFFFF"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(card_rect, r, r)
        p.end()
        super().paintEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._apply_round_clip()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._apply_round_clip()

    def media_widget(self) -> QWidget:
        return self._media

    @property
    def product_id(self) -> str:
        return self._product.id

    def _on_add(self) -> None:
        self.add_clicked.emit(self._product.id)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            add_pos = self._add_btn.mapFrom(self, pos)
            if self._add_btn.rect().contains(add_pos):
                super().mouseReleaseEvent(event)
                return
            self.clicked.emit(self._product.id)
        super().mouseReleaseEvent(event)


class KolomnaProdTile(QWidget):
    """prod-tile: сетка 2×N в menu-grid (референс)."""

    clicked = pyqtSignal(str)
    add_clicked = pyqtSignal(str)

    def __init__(self, product: Product, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._product = product
        self._m = metrics
        self._radius = metrics.radius
        self._media_h = scale(TILE_MEDIA_HEIGHT_PX, metrics.width)
        self._body_w = max(40, (metrics.width - metrics.gap * 3) // 2 - scale(64, metrics.width))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._clip_w = 0
        self._clip_h = 0

        self._card = QFrame()
        self._card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._card.setStyleSheet("QFrame { background: transparent; border: none; }")
        self._card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, self._shadow_bleed())
        outer.setSpacing(0)
        outer.addWidget(self._card)

        root = QVBoxLayout(self._card)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        border_css = "QFrame { background: #FFFFFF; border: none; }"
        col_w = max(scale(200, metrics.width), (metrics.width - metrics.gap * 3) // 2)
        media = KolomnaBerryArt(
            product,
            col_w,
            self._media_h,
            radius=0,
            bg="#FFFFFF",
            img_scale=1.16,
            fluid_width=True,
            ground_shadow=False,
            fit="cover",
        )
        self._media = media
        media_wrap = _TileMediaHost(media, self._media_h, border_css)
        root.addWidget(media_wrap)

        body = QWidget()
        body.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        body.setStyleSheet("background: transparent;")
        body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(
            scale(32, metrics.width),
            scale(30, metrics.width),
            scale(32, metrics.width),
            scale(32, metrics.width),
        )
        body_lay.setSpacing(scale(14, metrics.width))

        append_kolomna_product_titles(
            body_lay,
            product,
            metrics=metrics,
            title_px=metrics.fs_h3,
            body_w=self._body_w,
            title_weight=QFont.Weight.Black,
        )

        desc_raw = product_description(product) if load_kolomna_prefs().show_product_description else ""
        if desc_raw:
            desc_font = kolomna_font(metrics.fs_lead, QFont.Weight.Medium)
            desc_text, desc_h = _clamp_wrapped_text(
                desc_raw, desc_font, self._body_w, max_lines=2, line_height=1.3
            )
            d = QLabel(desc_text)
            d.setWordWrap(True)
            d.setMinimumWidth(0)
            d.setMaximumWidth(self._body_w)
            d.setFixedHeight(desc_h)
            d.setFont(desc_font)
            d.setStyleSheet(f"color: {INK_60}; background: transparent; line-height: 130%;")
            body_lay.addWidget(d)

        meta = QHBoxLayout()
        meta.setSpacing(scale(16, metrics.width))
        meta.addWidget(_PackChip(product_pack_label(product), metrics))
        meta.addStretch(1)
        body_lay.addLayout(meta)

        body_lay.addStretch(1)

        foot = QHBoxLayout()
        foot.setSpacing(scale(16, metrics.width))
        foot.setContentsMargins(0, scale(14, metrics.width), 0, 0)
        price = QLabel(f"{fmt_price(product.price_rub)}\u00a0{S.CUR}")
        price.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.Black))
        price.setStyleSheet(f"color: {GREEN}; background: transparent;")
        price.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        foot.addWidget(price, alignment=Qt.AlignmentFlag.AlignVCenter)
        add = _TileAddBtn(metrics)
        add.clicked.connect(self._on_add)
        self._add_btn = add
        foot.addWidget(add, alignment=Qt.AlignmentFlag.AlignVCenter)
        body_lay.addLayout(foot)
        root.addWidget(body)
        self._body = body

        self._sync_card_height(self._media_h + self._measure_body_height())

    def _measure_body_height(self) -> int:
        m = self._m
        bw = self._body_w
        pad_t = scale(30, m.width)
        pad_b = scale(32, m.width)
        gap = scale(14, m.width)
        total = pad_t + pad_b

        total += kolomna_product_titles_height(
            self._product,
            metrics=m,
            title_px=m.fs_h3,
            body_w=bw,
            title_weight=QFont.Weight.Black,
        )

        desc_raw = (
            product_description(self._product)
            if load_kolomna_prefs().show_product_description
            else ""
        )
        if desc_raw:
            total += gap
            desc_font = kolomna_font(m.fs_lead, QFont.Weight.Medium)
            _, desc_h = _clamp_wrapped_text(
                desc_raw, desc_font, bw, max_lines=2, line_height=1.3
            )
            total += desc_h

        total += gap
        chip_fs = scale(22, m.width)
        chip_pad_v = scale(10, m.width)
        chip_fm = QFontMetrics(kolomna_font(chip_fs, QFont.Weight.ExtraBold))
        total += chip_fm.height() + chip_pad_v * 2

        total += gap
        total += scale(14, m.width) + scale(TILE_ADD_BTN_MIN_HEIGHT_PX, m.width)
        return total

    def _shadow_bleed(self) -> int:
        return card_shadow_bleed(self._m)

    def content_height(self) -> int:
        return self._card_h + self._shadow_bleed()

    def _sync_card_height(self, card_h: int) -> None:
        self._card_h = max(self._media_h, card_h)
        self._card.setFixedHeight(self._card_h)
        self.setFixedHeight(self.content_height())
        self._clip_h = 0
        self._apply_round_clip()

    def set_row_height(self, total_h: int) -> None:
        """Высота ряда сетки: обе плитки в строке — как у более высокой."""
        self._sync_card_height(total_h - self._shadow_bleed())

    def _apply_round_clip(self) -> None:
        w = max(1, self._card.width())
        h = max(1, self._card.height())
        if w == self._clip_w and h == self._clip_h:
            return
        self._clip_w, self._clip_h = w, h
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), self._radius, self._radius)
        self._card.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = max(1, self.width())
        h = self._card_h
        r = float(self._radius)
        card_rect = QRectF(0, 0, w, h)
        _paint_card_shadow(p, card_rect, r, self._m)
        p.setBrush(QColor("#FFFFFF"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(card_rect, r, r)
        p.end()
        super().paintEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._apply_round_clip()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._apply_round_clip()

    def media_widget(self) -> QWidget:
        return self._media

    @property
    def product_id(self) -> str:
        return self._product.id

    def _on_add(self) -> None:
        self.add_clicked.emit(self._product.id)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            add_pos = self._add_btn.mapFrom(self, pos)
            if self._add_btn.rect().contains(add_pos):
                super().mouseReleaseEvent(event)
                return
            self.clicked.emit(self._product.id)
        super().mouseReleaseEvent(event)
