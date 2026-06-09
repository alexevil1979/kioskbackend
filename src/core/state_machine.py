from __future__ import annotations

from enum import Enum, auto

from PyQt6.QtCore import QObject, pyqtSignal


class AppScreen(Enum):
    START = auto()
    CATEGORIES = auto()
    TOURS = auto()
    MENU = auto()
    CART = auto()
    PAYMENT_METHOD = auto()
    PAYMENT_SBP = auto()
    PAYMENT_CARD = auto()
    SUCCESS = auto()
    PAYMENT_ERROR = auto()
    OFFLINE = auto()
    IDLE_WARNING = auto()


class NavigationController(QObject):
    screen_changed = pyqtSignal(AppScreen)

    def __init__(self) -> None:
        super().__init__()
        self._screen = AppScreen.START
        self._history: list[AppScreen] = []

    @property
    def current(self) -> AppScreen:
        return self._screen

    def go(self, screen: AppScreen, *, replace: bool = False) -> None:
        if not replace and self._screen != screen:
            self._history.append(self._screen)
        self._screen = screen
        self.screen_changed.emit(screen)

    def back(self) -> bool:
        if not self._history:
            return False
        self._screen = self._history.pop()
        self.screen_changed.emit(self._screen)
        return True

    def reset_to_menu(self) -> None:
        self._history.clear()
        self.go(AppScreen.MENU, replace=True)

    def reset_to_categories(self) -> None:
        self._history.clear()
        self.go(AppScreen.CATEGORIES, replace=True)

    def reset_to_start(self) -> None:
        self._history.clear()
        self.go(AppScreen.START, replace=True)
