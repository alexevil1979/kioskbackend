from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from PIL import Image

from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, KolomnaMetrics, scale


def pil_to_qpixmap(img: Image.Image) -> QPixmap:
    rgba = img.convert("RGBA")
    data = rgba.tobytes("raw", "RGBA")
    qimg = QImage(
        data,
        rgba.width,
        rgba.height,
        rgba.width * 4,
        QImage.Format.Format_RGBA8888,
    )
    return QPixmap.fromImage(qimg.copy())


class KolomnaReceiptPreviewDialog(QWidget):
    """Модальное окно: как будет выглядеть чек на принтере."""

    def __init__(self, metrics: KolomnaMetrics, pixmap: QPixmap, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._m = metrics
        self.setVisible(False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: rgba(20, 56, 33, 0.72);")

        pad = scale(48, metrics.width)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(pad, pad, pad, pad)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        box = QWidget()
        box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        box_w = min(scale(720, metrics.width), metrics.width - 2 * pad)
        box.setFixedWidth(box_w)
        box.setStyleSheet(
            f"background: {CREAM}; border-radius: {scale(32, metrics.width)}px;"
        )
        bl = QVBoxLayout(box)
        bl.setContentsMargins(scale(32, metrics.width), scale(28, metrics.width),
                              scale(32, metrics.width), scale(28, metrics.width))
        bl.setSpacing(scale(20, metrics.width))

        title = QLabel(S.ADMIN_PRINTER_PREVIEW_TITLE)
        title.setFont(kolomna_font(metrics.fs_body, QFont.Weight.ExtraBold))
        title.setStyleSheet(f"color: {GREEN}; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet(
            f"QScrollArea {{ background: {CREAM_DEEP}; border-radius: {scale(16, metrics.width)}px; }}"
        )
        paper = QLabel()
        paper.setObjectName("KolomnaReceiptPreviewPaper")
        self._paper_label = paper
        paper.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        paper.setPixmap(pixmap)
        paper.setStyleSheet("background: white; padding: 8px;")
        scroll.setWidget(paper)
        scroll.setMinimumHeight(scale(520, metrics.height))
        bl.addWidget(scroll)

        close_btn = QPushButton(S.ADMIN_PRINTER_PREVIEW_CLOSE)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFixedHeight(scale(72, metrics.width))
        close_btn.setFont(kolomna_font(metrics.fs_label, QFont.Weight.ExtraBold))
        close_btn.setStyleSheet(
            f"QPushButton {{ background: {GREEN}; color: {CREAM}; border: none; "
            f"border-radius: {scale(36, metrics.width)}px; font-weight: 800; }}"
            f"QPushButton:pressed {{ background: #163d22; }}"
        )
        close_btn.clicked.connect(self.hide)
        bl.addWidget(close_btn)

        outer.addWidget(box)

    def show_modal(self) -> None:
        self.setVisible(True)
        self.raise_()

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self._paper_label.setPixmap(pixmap)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and not self.childAt(event.pos()):
            self.hide()
        super().mousePressEvent(event)
