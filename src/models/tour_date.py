"""Даты и слоты экскурсий (GET /schedule → week_schedule.id)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class TourDate:
    pickup_schedule_id: int
    year: int
    month: int
    day: int
    date_display: str = ""
    start_time: str = ""
    end_time: str = ""

    @property
    def slot_id(self) -> str:
        return str(self.pickup_schedule_id)

    @classmethod
    def from_slot_id(cls, slot_id: str, slots: list[TourDate] | None = None) -> TourDate | None:
        if not slot_id:
            return None
        try:
            pid = int(slot_id)
        except ValueError:
            return cls._from_legacy_date(slot_id)
        if slots:
            for slot in slots:
                if slot.pickup_schedule_id == pid:
                    return slot
        return None

    @classmethod
    def _from_legacy_date(cls, slot_id: str) -> TourDate | None:
        parts = slot_id.split("-")
        if len(parts) != 3:
            return None
        try:
            y, m, d = (int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            return None
        if not (1 <= m <= 12 and 1 <= d <= 31):
            return None
        return cls(pickup_schedule_id=0, year=y, month=m, day=d)


def list_tour_dates_mock() -> list[TourDate]:
    """Доступные даты из i18n (офлайн / без API расписания)."""
    from src.ui import kolomna_strings as S

    year = date.today().year
    out: list[TourDate] = []
    for month, days in S.TOUR_DATES:
        for day in days:
            out.append(TourDate(pickup_schedule_id=0, year=year, month=month, day=day))
    return out


def format_tour_date(td: TourDate) -> str:
    if td.date_display:
        label = td.date_display
    else:
        from src.ui import kolomna_strings as S

        month_name = S.MONTHS_NOM.get(td.month, str(td.month))
        label = f"{td.day} {month_name.lower()}"
    if td.start_time:
        if td.end_time:
            return f"{label}, {td.start_time}–{td.end_time}"
        return f"{label}, {td.start_time}"
    return label
