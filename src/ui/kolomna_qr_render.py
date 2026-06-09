"""QR как в offline-референсе (qrcode-generator / кэш из Playwright)."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Literal

import qrcode
from src.core.config import ROOT
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap

LogoId = Literal["site", "tg", "vk", "max", ""]


def _draw_site_globe(p: QPainter, cx: float, cy: float, r: float) -> None:
    pen_w = max(1.5, r * 0.1)
    p.setPen(QPen(Qt.GlobalColor.white, pen_w))
    p.setBrush(Qt.BrushStyle.NoBrush)
    g = r * 0.62
    p.drawEllipse(int(cx - g), int(cy - g), int(2 * g), int(2 * g))
    p.drawEllipse(int(cx - g * 0.45), int(cy - g), int(2 * g * 0.45), int(2 * g))
    p.drawLine(int(cx - g), int(cy), int(cx + g), int(cy))


def _draw_tg_logo(p: QPainter, cx: float, cy: float, r: float) -> None:
    p.setBrush(QColor("#229ED9"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(int(cx - r), int(cy - r), int(2 * r), int(2 * r))
    p.setBrush(Qt.GlobalColor.white)
    path = QPainterPath()
    path.moveTo(cx - r * 0.55, cy + r * 0.05)
    path.lineTo(cx + r * 0.65, cy - r * 0.35)
    path.lineTo(cx - r * 0.05, cy + r * 0.05)
    path.lineTo(cx + r * 0.35, cy + r * 0.55)
    path.closeSubpath()
    p.drawPath(path)


def _draw_vk_logo(p: QPainter, cx: float, cy: float, r: float) -> None:
    p.setBrush(QColor("#0077FF"))
    p.setPen(Qt.PenStyle.NoPen)
    side = int(2 * r)
    p.drawRoundedRect(int(cx - r), int(cy - r), side, side, int(r * 0.42), int(r * 0.42))
    p.setPen(Qt.GlobalColor.white)
    f = QFont("Montserrat", max(8, int(r * 0.9)))
    f.setWeight(QFont.Weight.Black)
    p.setFont(f)
    p.drawText(int(cx - r), int(cy - r * 0.7), int(2 * r), int(2 * r), Qt.AlignmentFlag.AlignCenter, "VK")


def _draw_max_logo(p: QPainter, cx: float, cy: float, r: float) -> None:
    side = int(2 * r)
    x, y = int(cx - r), int(cy - r)
    grad = QLinearGradient(x, y + side, x + side, y)
    grad.setColorAt(0, Qt.GlobalColor.cyan)
    grad.setColorAt(1, Qt.GlobalColor.magenta)
    p.setBrush(grad)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(x, y, side, side, int(r * 0.42), int(r * 0.42))
    p.setBrush(Qt.GlobalColor.white)
    p.drawEllipse(int(cx - r * 0.45), int(cy - r * 0.35), int(r * 0.9), int(r * 0.7))


def _overlay_logo(p: QPainter, logo: LogoId, cx: float, cy: float, px: int) -> None:
    if not logo:
        return
    logo_r = px * 0.115
    pad_r = logo_r * 1.32
    p.setBrush(Qt.GlobalColor.white)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(int(cx - pad_r), int(cy - pad_r), int(2 * pad_r), int(2 * pad_r))
    if logo == "site":
        p.setBrush(QColor("#C8283C"))
        p.drawEllipse(int(cx - logo_r), int(cy - logo_r), int(2 * logo_r), int(2 * logo_r))
        _draw_site_globe(p, cx, cy, logo_r * 0.62)
    elif logo == "tg":
        _draw_tg_logo(p, cx, cy, logo_r)
    elif logo == "vk":
        _draw_vk_logo(p, cx, cy, logo_r)
    elif logo == "max":
        _draw_max_logo(p, cx, cy, logo_r)


def _cached_qr_path(kind: str, logo: LogoId, px: int) -> Path | None:
    d = ROOT / "assets" / "kolomna" / "qr"
    if kind == "info" and logo:
        for name in (f"info_{logo}_{px}.png", f"info_{logo}_460.png"):
            p = d / name
            if p.is_file():
                return p
        return None
    if kind == "pay":
        for name in (f"pay_sbp_{px}.png", "pay_sbp_560.png"):
            p = d / name
            if p.is_file():
                return p
        return None
    return None


def load_cached_qr_pixmap(kind: str, *, logo: LogoId = "", px: int = 460) -> QPixmap:
    path = _cached_qr_path(kind, logo, px)
    if not path:
        return QPixmap()
    pix = QPixmap(str(path))
    if pix.isNull():
        return QPixmap()
    if pix.width() != px and abs(pix.width() - px) > 1:
        return QPixmap()
    return pix


def render_kolomna_qr_pixmap(
    url: str,
    *,
    px: int = 460,
    color: str = "#1F4D2A",
    logo: LogoId = "",
) -> QPixmap:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,
        border=0,
    )
    qr.add_data(url)
    qr.make(fit=True)
    modules = qr.get_matrix()
    n = len(modules)
    margin = round(px * 0.045)
    cell = (px - margin * 2) / n

    img = QImage(px, px, QImage.Format.Format_RGB32)
    img.fill(QColor("#FFFFFF"))
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    p.setPen(Qt.PenStyle.NoPen)
    fill = QColor(color)
    p.setBrush(fill)
    for r in range(n):
        for c in range(n):
            if modules[r][c]:
                x = round(margin + c * cell)
                y = round(margin + r * cell)
                w = math.ceil(cell)
                h = math.ceil(cell)
                p.fillRect(x, y, w, h, fill)

    cx, cy = px / 2, px / 2
    _overlay_logo(p, logo, cx, cy, px)
    p.end()
    return QPixmap.fromImage(img)


def scale_qr_for_display(pix: QPixmap, display_px: int) -> QPixmap:
    if pix.isNull() or display_px <= 0:
        return QPixmap()
    return pix.scaled(
        display_px,
        display_px,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
