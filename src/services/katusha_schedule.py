"""Слоты экскурсий из GET /schedule."""
from __future__ import annotations

import logging
from datetime import date
from typing import Any

from src.models.tour_date import TourDate

logger = logging.getLogger(__name__)


def excursion_slots_from_schedule(
    data: dict[str, Any],
    schedule_location_id: int,
) -> list[TourDate]:
    """Слоты week_schedule для локации экскурсии из каталога."""
    if not schedule_location_id:
        return []
    out: list[TourDate] = []
    for loc in data.get("locations") or []:
        if not isinstance(loc, dict):
            continue
        try:
            loc_id = int(loc.get("id") or 0)
        except (TypeError, ValueError):
            continue
        if loc_id != schedule_location_id:
            continue
        for slot in loc.get("week_schedule") or []:
            parsed = _parse_week_slot(slot)
            if parsed is not None:
                out.append(parsed)
        break
    return out


def _parse_week_slot(slot: Any) -> TourDate | None:
    if not isinstance(slot, dict):
        return None
    try:
        pickup_schedule_id = int(slot.get("id") or 0)
    except (TypeError, ValueError):
        return None
    if pickup_schedule_id <= 0:
        return None

    date_s = str(slot.get("date") or "").strip()
    year = month = day = 0
    if date_s and len(date_s) >= 10:
        try:
            parts = date_s.split("-")
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        except (ValueError, IndexError):
            pass
    if not (year and 1 <= month <= 12 and 1 <= day <= 31):
        today = date.today()
        year, month, day = today.year, today.month, today.day

    return TourDate(
        pickup_schedule_id=pickup_schedule_id,
        year=year,
        month=month,
        day=day,
        date_display=str(slot.get("date_display") or "").strip(),
        start_time=str(slot.get("start_time") or "").strip(),
        end_time=str(slot.get("end_time") or "").strip(),
    )
