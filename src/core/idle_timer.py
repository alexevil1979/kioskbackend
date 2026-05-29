from __future__ import annotations

import logging

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from src.core.config import IdleConfig

logger = logging.getLogger(__name__)


class IdleTimer(QObject):
    """Таймер бездействия: предупреждение и сброс."""

    warning = pyqtSignal()
    reset = pyqtSignal()

    def __init__(self, config: IdleConfig, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._config = config
        self._active = True

        self._warning_timer = QTimer(self)
        self._warning_timer.setSingleShot(True)
        self._warning_timer.timeout.connect(self._on_warning)

        self._reset_timer = QTimer(self)
        self._reset_timer.setSingleShot(True)
        self._reset_timer.timeout.connect(self._on_reset)

    def bump(self) -> None:
        if not self._active:
            return
        self._warning_timer.stop()
        self._reset_timer.stop()
        warn_ms = max(1, self._config.warning_seconds) * 1000
        reset_ms = max(self._config.reset_seconds, self._config.warning_seconds + 1) * 1000
        self._warning_timer.start(warn_ms)
        self._reset_timer.start(reset_ms)

    def pause(self) -> None:
        self._active = False
        self._warning_timer.stop()
        self._reset_timer.stop()

    def resume(self) -> None:
        self._active = True
        self.bump()

    def dismiss_warning(self) -> None:
        """Пользователь нажал «Да, я здесь» — только сброс таймеров."""
        self.bump()

    def _on_warning(self) -> None:
        logger.info("Бездействие: показ предупреждения")
        self.warning.emit()

    def _on_reset(self) -> None:
        logger.info("Бездействие: сброс сессии")
        self.reset.emit()
