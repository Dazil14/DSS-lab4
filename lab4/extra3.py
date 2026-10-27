"""
E3 - One seat, two tickets

E3.1 Qoidani Session ta'minlashi kerak: bitta seansning BARCHA chiptalarini faqat Session biladi (Seat o'zi faqat
     joy, Ticket o'zi faqat o'zini biladi).
E3.2 Session.book(seat, customer) Ticket qaytaradi yoki joy sotilgan bo'lsa SeatTakenError beradi.
E3.4 Yetarli EMAS: 4 server har biri o'z Session obyektini xotirada ushlaydi, ikkisi bir vaqtda "joy bo'sh" deb
     ko'rib ikkalasi ham chipta yozishi mumkin (race condition). Bazaga UNIQUE (session_id, seat_id) cheklovi
     qo'shiladi (yoki qator qulfi / tranzaksiya) - faqat baza hamma serverlarning yozuvini ko'radi; ikkinchi INSERT
     IntegrityError beradi va u SeatTakenError'ga o'giriladi.
"""
from dataclasses import dataclass

import pytest


class SeatTakenError(Exception):
    """Bu joy shu seans uchun allaqachon sotilgan."""


@dataclass(frozen=True)
class Seat:
    row: str
    number: int


@dataclass(frozen=True)
class Customer:
    name: str


@dataclass(frozen=True)
class Ticket:
    seat: Seat
    customer: Customer


class Session:
    def __init__(self, title: str, seats):
        self.title = title
        self._seats = frozenset(seats)
        self._tickets: dict[Seat, Ticket] = {}   # "Seat 0..1 Ticket" shu lug'at bilan ta'minlanadi

    @property
    def tickets(self) -> tuple[Ticket, ...]:
        return tuple(self._tickets.values())

    def book(self, seat: Seat, customer: Customer) -> Ticket:
        if seat not in self._seats:
            raise ValueError(f"{seat} bu seansda yo'q")
        if seat in self._tickets:
            raise SeatTakenError(f"{seat} allaqachon sotilgan")
        ticket = Ticket(seat, customer)
        self._tickets[seat] = ticket
        return ticket


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
A1, A2 = Seat("A", 1), Seat("A", 2)
ALI, VALI = Customer("Ali"), Customer("Vali")


def make_session() -> Session:
    return Session("20:00 Dune", [A1, A2])


def test_booking_returns_ticket():
    ticket = make_session().book(A1, ALI)
    assert ticket == Ticket(A1, ALI)


def test_double_booking_raises_seat_taken_error():
    session = make_session()
    session.book(A1, ALI)
    with pytest.raises(SeatTakenError):
        session.book(A1, VALI)
    assert session.tickets == (Ticket(A1, ALI),)   # ikkinchi chipta yaratilmadi


def test_same_customer_cannot_book_same_seat_twice_either():
    session = make_session()
    session.book(A1, ALI)
    with pytest.raises(SeatTakenError):
        session.book(A1, ALI)


def test_different_seats_are_fine():
    session = make_session()
    session.book(A1, ALI)
    session.book(A2, VALI)
    assert len(session.tickets) == 2


def test_unknown_seat_is_rejected():
    with pytest.raises(ValueError):
        make_session().book(Seat("Z", 99), ALI)


def test_sessions_do_not_share_tickets():
    s1, s2 = make_session(), make_session()
    s1.book(A1, ALI)
    s2.book(A1, VALI)   # boshqa seans - xato emas


# --------------------------------------------------------------------------
# Done when:
#   [x] bir jarayonda ikki marta band qilish SeatTakenError beradi -> test_double_booking_raises_seat_taken_error
#   [x] bazadagi himoya: UNIQUE (session_id, seat_id), obyekt tekshiruvi nega yetarli emasligi E3.4 da tushuntirilgan
# --------------------------------------------------------------------------
