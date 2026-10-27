"""
E5 - Appointments five hours late

E5.1 Invariant: starts_at obyekt ichida har doim time zone'li (aware) va UTC'ga keltirilgan holda saqlanadi.
E5.2 Konstruktor naive datetime'ni ValueError bilan rad etadi (zona noma'lum - taxmin qilmaymiz).
E5.3 local_start(tz_name) UTC vaqtni so'ralgan zonaga o'giradi (zoneinfo). Windows'da: `pip install tzdata`.
E5.4 `now` parametr, chunki datetime.now() ichkarida bo'lsa natija haqiqiy soatga bog'lanadi: test har safar
     boshqa natija beradi (flaky) va chegara holatni (aniq 24 soat) tekshirib bo'lmaydi. Qat'iy `now` bilan test
     takrorlanadigan bo'ladi.
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

FREE_MOVE_WINDOW = timedelta(hours=24)


def _require_aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} time zone'li (aware) datetime bo'lishi kerak")


class Appointment:
    def __init__(self, patient, starts_at: datetime):
        _require_aware(starts_at, "starts_at")
        self.patient = patient
        self._starts_at = starts_at.astimezone(timezone.utc)  # invariant: har doim UTC

    @property
    def starts_at(self) -> datetime:
        return self._starts_at

    def local_start(self, tz_name: str) -> datetime:
        return self._starts_at.astimezone(ZoneInfo(tz_name))

    def is_movable(self, now: datetime) -> bool:
        """True - bepul ko'chirish mumkin (boshlanishiga kamida 24 soat bor)."""
        _require_aware(now, "now")
        return self._starts_at - now >= FREE_MOVE_WINDOW


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
TASHKENT = ZoneInfo("Asia/Tashkent")
START_LOCAL = datetime(2026, 11, 3, 9, 0, tzinfo=TASHKENT)


def test_naive_datetime_is_rejected():
    with pytest.raises(ValueError):
        Appointment("Ali", datetime(2026, 11, 3, 9, 0))


def test_nine_in_tashkent_is_stored_as_four_utc_and_shown_as_nine():
    appt = Appointment("Ali", START_LOCAL)
    assert appt.starts_at == datetime(2026, 11, 3, 4, 0, tzinfo=timezone.utc)
    assert appt.starts_at.utcoffset() == timedelta(0)
    shown = appt.local_start("Asia/Tashkent")
    assert (shown.hour, shown.minute) == (9, 0)


def test_other_timezone_input_gives_same_instant():
    utc_input = Appointment("Ali", datetime(2026, 11, 3, 4, 0, tzinfo=timezone.utc))
    assert utc_input.starts_at == Appointment("Ali", START_LOCAL).starts_at


def test_local_start_in_another_zone():
    assert Appointment("Ali", START_LOCAL).local_start("Europe/London").hour == 4


def test_24_hour_rule_with_fixed_now():
    appt = Appointment("Ali", START_LOCAL)
    exactly_24h = datetime(2026, 11, 2, 9, 0, tzinfo=TASHKENT)
    assert appt.is_movable(exactly_24h) is True                              # aniq 24 soat - hali bepul
    assert appt.is_movable(exactly_24h + timedelta(minutes=1)) is False     # 23 s 59 d - jarima
    assert appt.is_movable(datetime(2026, 10, 20, 9, 0, tzinfo=TASHKENT)) is True
    assert appt.is_movable(datetime(2026, 11, 3, 10, 0, tzinfo=TASHKENT)) is False  # boshlangan


def test_now_in_utc_works_too():
    appt = Appointment("Ali", START_LOCAL)
    assert appt.is_movable(datetime(2026, 11, 2, 4, 0, tzinfo=timezone.utc)) is True


def test_naive_now_is_rejected():
    with pytest.raises(ValueError):
        Appointment("Ali", START_LOCAL).is_movable(datetime(2026, 11, 1, 9, 0))


# --------------------------------------------------------------------------
# Done when:
#   [x] Appointment(patient, datetime(2026, 11, 3, 9, 0)) -> ValueError   -> test_naive_datetime_is_rejected
#   [x] 09:00 Toshkent = 04:00 UTC va local_start 09:00 ko'rsatadi        -> test_nine_in_tashkent_is_stored_as_four_utc_and_shown_as_nine
#   [x] 24 soatlik qoida qat'iy `now` bilan sinalgan                       -> test_24_hour_rule_with_fixed_now
# --------------------------------------------------------------------------
