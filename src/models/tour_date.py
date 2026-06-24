"""Даты экскурсий: mock сейчас, слоты API — позже."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class TourDate:
    year: int
    month: int
    day: int

    @property
    def slot_id(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    @classmethod
    def from_slot_id(cls, slot_id: str) -> TourDate | None:
        parts = slot_id.split("-")
        if len(parts) != 3:
            return None
        try:
            y, m, d = (int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            return None
        if not (1 <= m <= 12 and 1 <= d <= 31):
            return None
        return cls(y, m, d)


def list_tour_dates_mock() -> list[TourDate]:
    """Доступные даты из i18n (симуляция до API)."""
    from src.ui import kolomna_strings as S

    year = date.today().year
    out: list[TourDate] = []
    for month, days in S.TOUR_DATES:
        for day in days:
            out.append(TourDate(year=year, month=month, day=day))
    return out


def format_tour_date(td: TourDate) -> str:
    from src.ui import kolomna_strings as S

    month_name = S.MONTHS_NOM.get(td.month, str(td.month))
    return f"{td.day} {month_name.lower()}"
