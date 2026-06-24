from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QWidget

from src.ui.kolomna_chrome import chrome_top_pad
from src.ui.kolomna_tokens import CREAM, KolomnaMetrics, scale
from src.ui.widgets.kolomna_info_btn import KolomnaInfoButton
from src.ui.widgets.kolomna_lang_toggle import KolomnaLangToggle
from src.ui.widgets.kolomna_logo import LogoDrop


class KolomnaCatalogBar(QWidget):
    """catalog__bar: Инфо | logo-drop | lang-toggle — одна строка, верх по уровню кнопок."""

    info_clicked = pyqtSignal()
    admin_requested = pyqtSignal()
    lang_changed = pyqtSignal(str)

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        m = metrics
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {CREAM};")

        grid = QGridLayout(self)
        grid.setContentsMargins(m.pad, chrome_top_pad(m), m.pad, scale(28, m.width))
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 0)
        grid.setColumnStretch(2, 1)

        self._info = KolomnaInfoButton(m)
        self._info.clicked.connect(self.info_clicked.emit)
        self._info.admin_requested.connect(self.admin_requested.emit)
        grid.addWidget(self._info, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        logo_w = scale(340, m.width)
        logo_h = scale(158, m.width)
        self._logo = LogoDrop(logo_w, logo_h, admin_taps=True)
        self._logo.admin_requested.connect(self.admin_requested.emit)
        grid.addWidget(self._logo, 0, 1, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self._lang = KolomnaLangToggle(m.width)
        self._lang.lang_changed.connect(self.lang_changed.emit)
        grid.addWidget(self._lang, 0, 2, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

    def set_lang(self, lang: str) -> None:
        self._lang.set_lang(lang)

    def retranslate(self) -> None:
        self._info.retranslate()
        from src.ui.kolomna_i18n import get_lang

        self._lang.set_lang(get_lang())
