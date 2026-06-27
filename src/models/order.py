from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderCreateResult:
    order_id: int
    total_amount: float
    payment_method: str
    payment_id: str
    qr_code_payload: str
    qr_code_image: str = ""
    expires_in_seconds: int = 300


@dataclass(frozen=True)
class OrderStatusResult:
    order_id: int
    status: str
    payment_status: str
    paid: bool
    cancelled: bool
    total_amount: float


@dataclass(frozen=True)
class OrderReceiptResult:
    order_id: int
    receipt_text: str
    total_amount: float
    station_name: str = ""
    paid_at: str = ""
    pickup_qr_image: str = ""
    pickup_qr_available: bool = False
