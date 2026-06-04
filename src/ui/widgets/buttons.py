from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QSizePolicy


def primary_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("PrimaryBtn")
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


def secondary_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("SecondaryBtn")
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


def danger_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("DangerBtn")
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    return btn


def outline_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("OutlineBtn")
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    return btn


def category_button(text: str) -> QPushButton:
    """Pill-категория (.cat-pill в layout.css)."""
    btn = QPushButton(text)
    btn.setObjectName("CategoryBtn")
    btn.setCheckable(True)
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    btn.setFixedHeight(40)
    return btn


def add_to_cart_button() -> QPushButton:
    btn = QPushButton("Добавить")
    btn.setObjectName("AddToCartBtn")
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFixedHeight(40)
    btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return btn
