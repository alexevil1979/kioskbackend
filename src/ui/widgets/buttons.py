from __future__ import annotations

from PyQt6.QtWidgets import QPushButton


def primary_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("PrimaryBtn")
    btn.setMinimumHeight(64)
    return btn


def secondary_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("SecondaryBtn")
    btn.setMinimumHeight(64)
    return btn


def danger_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("DangerBtn")
    btn.setMinimumHeight(64)
    return btn


def outline_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("OutlineBtn")
    return btn
