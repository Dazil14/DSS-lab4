"""
Task 2 - Three different delivery fees

2.1  Qoida: food_total >= 150 000 -> bepul; aks holda 12 000 + 3 000 * (boshlangan km - 3). Qo'lda hisob:
       buyurtma             to'g'ri   Checkout   Receipt     Courier
       150 000 sum, 4.2 km        0       0 (OK)    15 000     0 (OK)
        90 000 sum, 4.2 km   18 000     15 000      15 000     ~15 600.0 (float)
        90 000 sum, 3.6 km   15 000     12 000      15 000 (OK) ~13 800.0 (float)
     Uchala holatda ham hamma uch servisni to'g'ri qiladigan yagona nusxa yo'q: Checkout km'ni kesib tashlaydi
     (int), Receipt yaxlitlaydi (round) va `>` bilan chegarani buzadi, Courier esa kasr km uchun pul to'laydi.
2.2  Information Expert: food_total va distance_km Order'da, shuning uchun qoida `Order.delivery_fee()` ichida;
     uch servis faqat shu metodni chaqiradi.
2.3  "Har bir boshlangan kilometr" = `math.ceil`. Pul int bo'lib qoladi (float yo'q).
2.4  Chegara testlari: 149 999 / 150 000 sum va 3.0 / 3.01 / 4.0 km - pastda.
"""
import math

import pytest


class Order:
    # Qoidaning hamma raqamlari BIR joyda: narx o'zgarsa - bitta qator o'zgaradi.
    FREE_DELIVERY_FROM = 150_000
    BASE_FEE = 12_000
    BASE_KM = 3
    EXTRA_KM_FEE = 3_000

    def __init__(self, food_total: int, distance_km: float):
        if food_total < 0 or distance_km < 0:
            raise ValueError("food_total va distance_km manfiy bo'lishi mumkin emas")
        self.food_total = food_total
        self.distance_km = distance_km

    def delivery_fee(self) -> int:
        if self.food_total >= self.FREE_DELIVERY_FROM:
            return 0
        extra_km = max(0, math.ceil(self.distance_km) - self.BASE_KM)  # boshlangan km
        return self.BASE_FEE + extra_km * self.EXTRA_KM_FEE


class CheckoutService:
    def delivery_fee(self, order: Order) -> int:
        return order.delivery_fee()


class ReceiptService:
    def delivery_fee(self, order: Order) -> int:
        return order.delivery_fee()


class CourierPayoutService:
    def delivery_fee(self, order: Order) -> int:
        return order.delivery_fee()


SERVICES = [CheckoutService(), ReceiptService(), CourierPayoutService()]


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "food_total, distance_km, expected",
    [
        # 2.1: qo'lda hisoblangan uchta buyurtma
        (150_000, 4.2, 0),
        (90_000, 4.2, 18_000),
        (90_000, 3.6, 15_000),
        # 2.4: summa chegarasi
        (149_999, 3.0, 12_000),
        (150_000, 3.0, 0),
        (149_999, 10.0, 12_000 + 7 * 3_000),
        (150_000, 10.0, 0),
        # 2.4: masofa chegarasi
        (90_000, 3.0, 12_000),
        (90_000, 3.01, 15_000),
        (90_000, 4.0, 15_000),
        (90_000, 0.5, 12_000),
    ],
)
def test_fee_rule_and_boundaries(food_total, distance_km, expected):
    assert Order(food_total, distance_km).delivery_fee() == expected


def test_fee_is_int_not_float():
    assert type(Order(90_000, 4.2).delivery_fee()) is int


@pytest.mark.parametrize("service", SERVICES, ids=lambda s: type(s).__name__)
@pytest.mark.parametrize("food_total, distance_km", [(150_000, 4.2), (90_000, 4.2), (90_000, 3.6)])
def test_all_services_return_the_same_fee(service, food_total, distance_km):
    order = Order(food_total, distance_km)
    assert service.delivery_fee(order) == order.delivery_fee()


def test_changing_extra_km_fee_is_a_one_line_change(monkeypatch):
    monkeypatch.setattr(Order, "EXTRA_KM_FEE", 3_500)  # bitta qiymat o'zgardi
    order = Order(90_000, 4.2)  # 2 ta boshlangan qo'shimcha km
    assert [s.delivery_fee(order) for s in SERVICES] == [19_000] * 3


def test_negative_input_is_rejected():
    with pytest.raises(ValueError):
        Order(-1, 2.0)
    with pytest.raises(ValueError):
        Order(10_000, -0.1)


# --------------------------------------------------------------------------
# Done when:
#   [x] qoida faqat Order.delivery_fee() ichida (uch servis uni chaqiradi)
#   [x] chegara testlari o'tadi              -> test_fee_rule_and_boundaries
#   [x] 3 000 -> 3 500 bitta qator           -> Order.EXTRA_KM_FEE, test_changing_extra_km_fee_is_a_one_line_change
# --------------------------------------------------------------------------
