"""
Task 10 - Three thousand test SMS

10.1 Hozirgi munosabat - COMPOSITION: ReminderService konstruktorida SmsClient'ni O'ZI yaratadi va unga egalik
     qiladi. Bu noto'g'ri: SMS klient servisning "qismi" emas, balki tashqi resurs (provayder, kalit) - uning umri
     servis umriga bog'lanmasligi kerak; ustiga servis aniq klassga qotib qolgan (qattiq coupling), shuning uchun
     testda soxta klientni qo'yib bo'lmaydi.
10.2 Klient tashqaridan beriladi (konstruktor argumenti, dependency injection) - munosabat association bo'ladi.
     Haqiqiy SmsClient ilova kirish nuqtasida (`build_reminder_service`, "composition root") yaratiladi, kalit
     SMS_API_KEY muhit o'zgaruvchisidan olinadi - manba kodda kalit yo'q.
10.3 FakeSmsClient xabarlarni ro'yxatga yozadi; test shu ro'yxatni tekshiradi va "REAL SMS" chiqmasligini ham.
10.4 Boshqa production muammosi: `send` birinchi xatoda (tarmoq/provayder) butun siklni to'xtatadi - qolgan bemorlar
     eslatma olmaydi, jo'natilganlar esa qayta ishga tushganda ikkinchi marta SMS oladi (xatolarni qayta ishlash va
     "yuborildi" belgisi yo'q). Qo'shimcha: prod kalit manba kodda (git'ga tushadi) edi - u olib tashlandi.
"""
import os
from typing import Protocol

import pytest


class SmsSender(Protocol):
    def send(self, phone: str, text: str) -> None: ...


class SmsClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def send(self, phone, text):
        # production'da bu yerda SMS provayderning HTTP API'si chaqiriladi
        print(f"REAL SMS to {phone}: {text}")


class ReminderService:
    def __init__(self, sms: SmsSender):
        self._sms = sms  # tashqaridan beriladi; servis o'zi SmsClient yaratmaydi

    def remind(self, appointments):
        for a in appointments:
            text = f"Reminder: your visit tomorrow at {a['time']}"
            self._sms.send(a["phone"], text)


def build_reminder_service() -> ReminderService:
    """Composition root: haqiqiy klient FAQAT shu yerda yaratiladi."""
    api_key = os.environ.get("SMS_API_KEY")
    if not api_key:
        raise RuntimeError("SMS_API_KEY muhit o'zgaruvchisi o'rnatilmagan")
    return ReminderService(SmsClient(api_key=api_key))


class FakeSmsClient:
    """Test uchun: hech narsa yubormaydi, faqat yozib boradi."""

    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    def send(self, phone, text):
        self.sent.append((phone, text))


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
def test_two_appointments_produce_two_messages(capsys):
    fake = FakeSmsClient()
    service = ReminderService(fake)
    service.remind(
        [
            {"phone": "+998901234567", "time": "09:00"},
            {"phone": "+998935550000", "time": "14:30"},
        ]
    )
    assert fake.sent == [
        ("+998901234567", "Reminder: your visit tomorrow at 09:00"),
        ("+998935550000", "Reminder: your visit tomorrow at 14:30"),
    ]
    assert "REAL SMS" not in capsys.readouterr().out


def test_no_appointments_no_messages():
    fake = FakeSmsClient()
    ReminderService(fake).remind([])
    assert fake.sent == []


def test_service_cannot_create_a_client_by_itself():
    with pytest.raises(TypeError):
        ReminderService()  # klient majburiy argument


def test_factory_requires_api_key_from_environment(monkeypatch):
    monkeypatch.delenv("SMS_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SMS_API_KEY"):
        build_reminder_service()


# --------------------------------------------------------------------------
# Done when:
#   [x] test faqat soxta klientdan foydalanadi        -> test_two_appointments_produce_two_messages
#   [x] ReminderService hech qachon SmsClient yaratmaydi -> test_service_cannot_create_a_client_by_itself
#   [x] manba kodda API kalit yo'q (kalit muhit o'zgaruvchisidan olinadi)
# --------------------------------------------------------------------------
