"""
Task 1 - The cart that belongs to everybody

1.2  Ikkita xato bor: `items = []` (klass atributi) va `coupons=[]` (default argument). Ildiz sabab bitta:
     o'zgaruvchan ro'yxat BIR MARTA yaratiladi (klass / funksiya e'lon qilinganda) va barcha obyektlar
     shu bitta ro'yxatni baham ko'radi.
1.3  Tuzatish: ro'yxat har bir obyekt uchun __init__ ichida yaratiladi, default esa None. @dataclass'da
     `coupons: list = []` yozsak ValueError ("mutable default ... use default_factory") chiqadi;
     o'rniga `field(default_factory=list)` yoziladi.
1.4  `self.items.append(...)` atributni qayta bog'lamaydi: obyektda `items` yo'q, Python uni klassdan topadi va
     hamma savat uchun umumiy bo'lgan o'sha ro'yxatni o'zgartiradi. `self.count += 1` esa
     `self.count = self.count + 1` ga teng: qiymat klassdan o'qiladi, lekin yangi int obyektni YOZISH
     faqat shu instansiyada yangi atribut yaratadi.
"""
from dataclasses import dataclass, field

import pytest


# --------------------------------------------------------------------------
# 1.3 Tuzatilgan oddiy klass
# --------------------------------------------------------------------------
class Cart:
    def __init__(self, user_id, coupons=None):
        self.user_id = user_id
        self.items = list()  # har bir savat o'zining yangi ro'yxatiga ega
        # tashqaridan kelgan ro'yxatning NUSXASI olinadi (aliasing yo'q)
        self.coupons = list(coupons) if coupons is not None else list()

    def add(self, sku, qty=1):
        self.items.append((sku, qty))

    def apply_coupon(self, code):
        self.coupons.append(code)


# --------------------------------------------------------------------------
# 1.3 Xuddi shu klass @dataclass sifatida
# --------------------------------------------------------------------------
@dataclass
class CartDataclass:
    user_id: str
    coupons: list[str] = field(default_factory=list)
    items: list[tuple[str, int]] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.coupons = list(self.coupons)  # tashqi ro'yxatdan nusxa

    def add(self, sku, qty=1):
        self.items.append((sku, qty))

    def apply_coupon(self, code):
        self.coupons.append(code)


CART_CLASSES = [Cart, CartDataclass]


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
def make_buggy_cart_class():
    """Ticket #4127'dagi ASL (xato) kod. Har chaqiruvda yangi klass qaytadi, shuning uchun
    uning umumiy holati boshqa testlarga ta'sir qilmaydi."""

    class BuggyCart:
        items = []

        def __init__(self, user_id, coupons=[]):
            self.user_id = user_id
            self.coupons = coupons

        def add(self, sku, qty=1):
            self.items.append((sku, qty))

        def apply_coupon(self, code):
            self.coupons.append(code)

    return BuggyCart


def check_second_cart_is_empty(cart_cls):
    """1.1: ticketni qayta ishlab chiqaradi."""
    first = cart_cls("user-1")
    second = cart_cls("user-2")
    first.add("A1", 2)
    first.apply_coupon("SALE10")
    assert second.items == [], "ikkinchi foydalanuvchi birinchisining mahsulotini ko'ryapti"
    assert second.coupons == [], "ikkinchi foydalanuvchi birinchisining kuponini ko'ryapti"


@pytest.mark.parametrize("cart_cls", CART_CLASSES)
def test_ticket_4127_second_cart_stays_empty(cart_cls):
    check_second_cart_is_empty(cart_cls)


def test_ticket_4127_test_fails_on_original_code():
    # Xuddi shu tekshiruv ESKI kodda yiqiladi - demak test xatoni haqiqatan ushlaydi.
    with pytest.raises(AssertionError):
        check_second_cart_is_empty(make_buggy_cart_class())


@pytest.mark.parametrize("cart_cls", CART_CLASSES)
def test_two_carts_never_share_a_list(cart_cls):
    first, second = cart_cls("u1"), cart_cls("u2")
    assert first.items is not second.items
    assert first.coupons is not second.coupons


@pytest.mark.parametrize("cart_cls", CART_CLASSES)
def test_constructor_copies_the_coupon_list(cart_cls):
    outside = ["WELCOME"]
    cart = cart_cls("u1", outside)
    outside.append("HACK")
    assert cart.coupons == ["WELCOME"]


def test_dataclass_rejects_mutable_default():
    # 1.3: `coupons: list = []` (yoki list()) dataclass'da ValueError beradi
    with pytest.raises(ValueError, match="mutable default"):

        @dataclass
        class BadCart:
            coupons: list = list()


def test_append_changes_shared_list_but_plus_equals_creates_instance_attribute():
    # 1.4
    class Demo:
        shared = list()
        count = 0

        def bump(self):
            self.count += 1  # self.count = self.count + 1 -> instansiyaga yozadi

    a, b = Demo(), Demo()
    a.shared.append("x")                      # klassdagi bitta ro'yxat o'zgaradi
    assert b.shared == ["x"]
    a.bump()
    assert a.count == 1 and b.count == 0 and Demo.count == 0
    assert "count" in vars(a) and "count" not in vars(b)


# --------------------------------------------------------------------------
# Done when:
#   [x] test o'tadi                       -> test_ticket_4127_second_cart_stays_empty
#   [x] ikki savat ro'yxat ulashmaydi     -> test_two_carts_never_share_a_list
#   [x] klass tanasida / default argumentda [] yoki {} yo'q (Cart va CartDataclass'da list() / default_factory)
# --------------------------------------------------------------------------
