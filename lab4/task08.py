"""
Task 8 - Somebody changed my order

8.1  (a) ALIASING: konstruktor tashqaridan kelgan ro'yxatning o'zini saqlaydi - `cart_lines` va `order.lines` bitta
     ro'yxatga ikkita nom, shuning uchun savat keyin o'zgartirsa buyurtma ham o'zgaradi. (b) Order o'z qatorlariga
     egalik qilishi kerak (COMPOSITION), lekin `lines` ochiq o'zgaruvchan ro'yxat: promo modul `order.lines.append(...)`
     bilan Order'ning qoidalarini (status) chetlab o'tadi - qismni faqat butun o'zgartirishi kerak edi.
8.2  Konstruktor qatorlarni NUSXALAYDI (har biri o'zgarmas NamedTuple), `lines` esa tashqariga faqat o'qish uchun
     tuple beradi - `.append` AttributeError.
8.3  add_line qty < 1 ni rad etadi (ValueError) va confirm()'dan keyin OrderLockedError beradi.
8.4  Bo'sh buyurtmani confirm() tekshiradi: faqat shu metod draft -> confirmed o'tish lahzasini biladi.
"""
from typing import NamedTuple

import pytest


class OrderLockedError(Exception):
    """Tasdiqlangan buyurtmani o'zgartirishga urinish."""


class EmptyOrderError(ValueError):
    """Qatorsiz buyurtmani tasdiqlab bo'lmaydi."""


class OrderLine(NamedTuple):
    sku: str
    qty: int
    unit_price: int


def _make_line(sku, qty, unit_price) -> OrderLine:
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty int bo'lishi kerak")
    if qty < 1:
        raise ValueError("qty kamida 1 bo'lishi kerak")
    if isinstance(unit_price, bool) or not isinstance(unit_price, int) or unit_price < 0:
        raise ValueError("unit_price manfiy bo'lmagan int bo'lishi kerak")
    return OrderLine(sku, qty, unit_price)


class Order:
    def __init__(self, order_id, lines):
        self._order_id = order_id
        self._status = "draft"
        # NUSXA: tashqi ro'yxatga bog'lanmaymiz (aliasing yo'q)
        self._lines: list[OrderLine] = [_make_line(*line) for line in lines]

    @property
    def order_id(self):
        return self._order_id

    @property
    def status(self) -> str:
        return self._status

    @property
    def lines(self) -> tuple[OrderLine, ...]:
        return tuple(self._lines)  # faqat o'qish uchun ko'rinish

    def total(self) -> int:
        return sum(qty * price for _, qty, price in self._lines)

    def add_line(self, sku, qty, unit_price) -> None:
        if self._status != "draft":
            raise OrderLockedError(f"buyurtma {self._status}, o'zgartirib bo'lmaydi")
        self._lines.append(_make_line(sku, qty, unit_price))

    def confirm(self) -> None:
        if not self._lines:
            raise EmptyOrderError("qatorsiz buyurtmani tasdiqlab bo'lmaydi")
        self._status = "confirmed"


def run_scenario() -> int:
    """Vazifadagi skript."""
    cart_lines = [("A1", 2, 50_000)]
    order = Order(1001, cart_lines)
    order.confirm()
    cart_lines.append(("B7", 1, 30_000))  # savat ishlashda davom etadi
    return order.total()


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
def test_script_gives_100000():
    assert run_scenario() == 100_000


def test_cart_list_is_copied_not_aliased():
    cart_lines = [("A1", 2, 50_000)]
    order = Order(1, cart_lines)
    cart_lines.append(("B7", 1, 30_000))
    assert order.lines == (OrderLine("A1", 2, 50_000),)
    assert order.total() == 100_000


def test_lines_are_read_only_from_outside():
    order = Order(1, [("A1", 2, 50_000)])
    with pytest.raises(AttributeError):
        order.lines.append(("B7", 1, 30_000))
    with pytest.raises(TypeError):
        order.lines[0] = ("B7", 1, 30_000)
    with pytest.raises(AttributeError):
        order.lines = ()
    assert order.total() == 100_000


def test_lines_snapshot_does_not_change_later():
    order = Order(1, [("A1", 2, 50_000)])
    before = order.lines
    order.add_line("B7", 1, 30_000)
    assert len(before) == 1 and len(order.lines) == 2


def test_add_line_works_in_draft():
    order = Order(1, [])
    order.add_line("A1", 3, 10_000)
    assert order.total() == 30_000


@pytest.mark.parametrize("qty", [0, -1])
def test_add_line_rejects_qty_below_one(qty):
    order = Order(1, [("A1", 1, 1_000)])
    with pytest.raises(ValueError):
        order.add_line("B7", qty, 5_000)
    assert len(order.lines) == 1


def test_add_line_after_confirm_raises_order_locked_error():
    order = Order(1, [("A1", 2, 50_000)])
    order.confirm()
    with pytest.raises(OrderLockedError):
        order.add_line("B7", 1, 30_000)
    assert order.total() == 100_000 and order.status == "confirmed"


def test_confirming_empty_order_raises_error():
    order = Order(1, [])
    with pytest.raises(EmptyOrderError):
        order.confirm()
    assert order.status == "draft"


def test_constructor_validates_lines_too():
    with pytest.raises(ValueError):
        Order(1, [("A1", 0, 1_000)])


# --------------------------------------------------------------------------
# Done when:
#   [x] skript 100000 chiqaradi                 -> test_script_gives_100000
#   [x] order.lines.append(...) mumkin emas      -> test_lines_are_read_only_from_outside
#   [x] confirm()'dan keyin add_line -> OrderLockedError -> test_add_line_after_confirm_raises_order_locked_error
#   [x] bo'sh buyurtmani confirm qilish xato beradi -> test_confirming_empty_order_raises_error
# --------------------------------------------------------------------------
if __name__ == "__main__":
    print(run_scenario())  # 100000
