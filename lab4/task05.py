"""
Task 5 - Validation without touching 40 call sites

5.1  price va discount_percent property + setter bo'ldi: `product.price = ...` yozuvi o'zgarmadi (40 joy tegilmaydi),
     lekin endi har bir yozish setter orqali tekshiriladi. price: int > 0; discount_percent: int, 0..90.
5.2  Konstruktor qiymatni `self.price = price` bilan yozadi, ya'ni o'sha setter'dan o'tadi - shuning uchun
     `Product('A1', -5)` ham rad etiladi (qiymat -> ValueError, tur int emas -> TypeError).
5.3  final_price butun sonlarda hisoblanadi: `price * (100 - discount) // 100` - int va pastga yaxlitlangan
     (99 990, 15% -> 84 991).
5.4  Teammate'ning g'oyasi: yakuniy narx __init__'da bir marta hisoblanib atributda saqlanadi - narx keyin o'zgarsa
     u ESKIRIB qoladi (pastdagi test: p.price = 200_000 dan keyin ham final 90_000 qoladi, to'g'risi 180_000).
5.5  `sku` faqat `_sku` + property (setter yo'q): `p.sku = 'X'` -> AttributeError.
"""
import pytest


def _require_int(name, value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} int bo'lishi kerak, {type(value).__name__} berildi")
    return value


class Product:
    def __init__(self, sku, price, discount_percent=0):
        if not isinstance(sku, str):
            raise TypeError("sku str bo'lishi kerak")
        if not sku:
            raise ValueError("sku bo'sh bo'lishi mumkin emas")
        self._sku = sku
        self.price = price                      # setter orqali tekshiriladi
        self.discount_percent = discount_percent  # setter orqali tekshiriladi

    @property
    def sku(self):
        return self._sku  # setter yo'q -> o'zgartirib bo'lmaydi

    @property
    def price(self) -> int:
        return self._price

    @price.setter
    def price(self, value):
        _require_int("price", value)
        if value <= 0:
            raise ValueError("price 0 dan katta bo'lishi kerak")
        self._price = value

    @property
    def discount_percent(self) -> int:
        return self._discount_percent

    @discount_percent.setter
    def discount_percent(self, value):
        _require_int("discount_percent", value)
        if not 0 <= value <= 90:
            raise ValueError("discount_percent 0..90 oralig'ida bo'lishi kerak")
        self._discount_percent = value

    def final_price(self) -> int:
        # faqat butun sonlar: natija int va pastga yaxlitlangan (so'mda)
        return self._price * (100 - self._discount_percent) // 100


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
def test_price_zero_is_rejected():
    p = Product("A1", 100_000)
    with pytest.raises(ValueError):
        p.price = 0


def test_discount_150_is_rejected():
    p = Product("A1", 100_000)
    with pytest.raises(ValueError):
        p.discount_percent = 150


def test_constructor_validates_too():
    with pytest.raises(ValueError):
        Product("A1", -5)
    with pytest.raises(ValueError):
        Product("A1", 0)
    with pytest.raises(ValueError):
        Product("A1", 100_000, 150)


def test_old_assignment_line_still_works():
    p = Product("A1", 100_000)
    p.price = 120_000          # 40 ta joydagi eski yozuv o'zgarmaydi
    p.discount_percent = 10
    assert p.price == 120_000 and p.discount_percent == 10


@pytest.mark.parametrize("bad", [12.5, "100", None, True])
def test_wrong_types_raise_type_error(bad):
    p = Product("A1", 100_000)
    with pytest.raises(TypeError):
        p.price = bad
    with pytest.raises(TypeError):
        p.discount_percent = bad


@pytest.mark.parametrize("value", [-1, 91, 150])
def test_discount_out_of_range(value):
    with pytest.raises(ValueError):
        Product("A1", 100_000).discount_percent = value


@pytest.mark.parametrize("value", [0, 90])
def test_discount_boundaries_are_allowed(value):
    p = Product("A1", 100_000, value)
    assert p.discount_percent == value


def test_final_price_is_int_rounded_down():
    price = Product("A1", 99_990, 15).final_price()
    assert price == 84_991 and type(price) is int  # ilgari 84991.5


def test_sku_is_read_only():
    p = Product("A1", 100_000)
    with pytest.raises(AttributeError):
        p.sku = "X"
    assert p.sku == "A1"


def test_cached_final_price_goes_stale_but_method_does_not():
    class CachedProduct:  # teammate'ning g'oyasi
        def __init__(self, price, discount):
            self.price = price
            self.final = price * (100 - discount) // 100  # bir marta hisoblandi

    cached = CachedProduct(100_000, 10)
    cached.price = 200_000
    assert cached.final == 90_000          # eskirgan! to'g'risi 180_000

    real = Product("A1", 100_000, 10)
    real.price = 200_000
    assert real.final_price() == 180_000   # metod har safar yangidan hisoblaydi


# --------------------------------------------------------------------------
# Done when:
#   [x] p.price = 0, p.discount_percent = 150, Product('A1', -5) -> ValueError
#   [x] p.price = 120_000 hali ishlaydi
#   [x] p.sku = 'X' -> AttributeError
# --------------------------------------------------------------------------
