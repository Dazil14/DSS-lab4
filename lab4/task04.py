"""
Task 4 - The negative balance in production

4.1  10.5 -> TypeError (tur noto'g'ri), -10 -> ValueError (tur to'g'ri, qiymat noto'g'ri). `deposit(True)`: oddiy
     `isinstance(amount, int)` uni QABUL QILARDI (bool - int'ning bolasi, True == 1 tiyin); mening kodim bool'ni
     alohida tekshirib TypeError beradi.
4.2  `balance` va `history` faqat property (setter yo'q); history tuple'lar tuple'i sifatida beriladi, shuning uchun
     `.append` AttributeError, `[0] = ...` TypeError beradi. `wallet.balance -= 500` -> AttributeError.
4.3  Refund - uchinchi tur ("refund"). (Taxmin: refund = bekor qilingan xarid puli hamyonga QAYTADI, balans ortadi.)
     Balansga deposit kabi ta'sir qiladi, lekin bu yangi pul emas - oldingi to'lovning teskarisi. Tarix farqni bilishi
     kerak: buxgalteriya, soliq, firibgarlik tekshiruvi va to'lov provayderi bilan solishtirish uchun.
4.4  Float noto'g'ri: `0.1 + 0.2 == 0.30000000000000004`, chunki 0.1 ikkilik tizimda aniq saqlanmaydi. Tiyinda int:
     `10 + 20 == 30` - butun sonlar aniq saqlanadi va qo'shiladi.
"""
import random

import pytest


class InsufficientFundsError(ValueError):
    """Balans yetarli emas."""


class Wallet:
    """Invariantlar: balans int (tiyin) va >= 0; faqat deposit/withdraw/refund o'zgartiradi;
    har bir o'zgarish tarixga (kind, amount, balance_after) sifatida yoziladi."""

    def __init__(self, owner_id, balance: int = 0):
        self._owner_id = owner_id
        self._balance = 0
        self._history: list[tuple[str, int, int]] = []
        self._check_int(balance)
        if balance < 0:
            raise ValueError("boshlang'ich balans manfiy bo'lishi mumkin emas")
        if balance > 0:
            self._record("opening", balance)

    # --- faqat o'qish uchun ---------------------------------------------
    @property
    def owner_id(self):
        return self._owner_id

    @property
    def balance(self) -> int:
        return self._balance

    @property
    def history(self) -> tuple[tuple[str, int, int], ...]:
        return tuple(self._history)  # o'zgarmas nusxa

    # --- yagona yo'llar --------------------------------------------------
    def deposit(self, amount: int) -> None:
        self._record("deposit", self._check_amount(amount))

    def withdraw(self, amount: int) -> None:
        self._check_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError(f"balans {self._balance}, so'ralgan {amount}")
        self._record("withdraw", -amount)

    def refund(self, amount: int) -> None:
        self._record("refund", self._check_amount(amount))

    # --- ichki yordamchilar ---------------------------------------------
    @staticmethod
    def _check_int(value) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"int (tiyin) kutilgan, {type(value).__name__} berildi")
        return value

    @classmethod
    def _check_amount(cls, amount) -> int:
        cls._check_int(amount)
        if amount <= 0:
            raise ValueError("amount musbat bo'lishi kerak")
        return amount

    def _record(self, kind: str, delta: int) -> None:
        new_balance = self._balance + delta
        assert new_balance >= 0  # invariant: yuqoridagi tekshiruvlardan keyin buzilmaydi
        self._balance = new_balance
        self._history.append((kind, abs(delta), new_balance))


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
def test_admin_script_line_raises_attribute_error():
    wallet = Wallet("u1", 10_000)
    with pytest.raises(AttributeError):
        wallet.balance -= 500  # intsident sababi bo'lgan qator
    assert wallet.balance == 10_000


def test_history_cannot_be_changed_from_outside():
    wallet = Wallet("u1")
    wallet.deposit(100)
    with pytest.raises(AttributeError):
        wallet.history.append(("deposit", 1, 1))
    with pytest.raises(TypeError):
        wallet.history[0] = ("deposit", 999, 999)
    with pytest.raises(AttributeError):
        wallet.history = ()
    assert wallet.history == (("deposit", 100, 100),)


def test_deposit_withdraw_refund_are_written_to_history():
    wallet = Wallet("u1")
    wallet.deposit(1_000)
    wallet.withdraw(300)
    wallet.refund(50)
    assert wallet.balance == 750
    assert wallet.history == (
        ("deposit", 1_000, 1_000),
        ("withdraw", 300, 700),
        ("refund", 50, 750),
    )


@pytest.mark.parametrize("method", ["deposit", "withdraw", "refund"])
@pytest.mark.parametrize("bad", [10.5, "10", None, True, False])
def test_wrong_type_raises_type_error(method, bad):
    wallet = Wallet("u1", 1_000)
    with pytest.raises(TypeError):
        getattr(wallet, method)(bad)  # deposit(True) ham rad etiladi
    assert wallet.balance == 1_000


@pytest.mark.parametrize("method", ["deposit", "withdraw", "refund"])
@pytest.mark.parametrize("bad", [-10, 0])
def test_non_positive_amount_raises_value_error(method, bad):
    wallet = Wallet("u1", 1_000)
    with pytest.raises(ValueError):
        getattr(wallet, method)(bad)
    assert wallet.balance == 1_000


def test_overdraft_is_rejected_and_changes_nothing():
    wallet = Wallet("u1", 500)
    with pytest.raises(InsufficientFundsError):
        wallet.withdraw(501)
    assert wallet.balance == 500
    assert wallet.history == (("opening", 500, 500),)


def test_no_sequence_of_calls_makes_balance_negative():
    rng = random.Random(2026)
    wallet = Wallet("u1")
    for _ in range(3_000):
        method = rng.choice([wallet.deposit, wallet.withdraw, wallet.refund])
        amount = rng.choice([rng.randint(-20, 400), 10.5, "5", True])
        try:
            method(amount)
        except (TypeError, ValueError):
            pass
        assert wallet.balance >= 0
    # tarixni qayta o'ynasak, aynan hozirgi balans chiqadi
    replay = 0
    for kind, amount, balance_after in wallet.history:
        replay += -amount if kind == "withdraw" else amount
        assert replay == balance_after
    assert replay == wallet.balance


def test_negative_or_float_opening_balance_is_rejected():
    with pytest.raises(ValueError):
        Wallet("u1", -1)
    with pytest.raises(TypeError):
        Wallet("u1", 0.0)


def test_float_is_wrong_for_money_but_int_tiyin_is_exact():
    assert 0.1 + 0.2 != 0.3          # 0.30000000000000004
    assert 10 + 20 == 30             # tiyinda int: aniq


# --------------------------------------------------------------------------
# Done when:
#   [x] wallet.balance -= 500 -> AttributeError  -> test_admin_script_line_raises_attribute_error
#   [x] hech qanday ketma-ketlik manfiy qilmaydi -> test_no_sequence_of_calls_makes_balance_negative
#   [x] tarixni tashqaridan o'zgartirib bo'lmaydi -> test_history_cannot_be_changed_from_outside
# --------------------------------------------------------------------------
