"""
E4 - The lost phone number

E4.1 Muammo: ikkala ekran repo.get(42) chaqirib ikki alohida Customer oladi; birinchisi yangi telefonni saqlaydi,
     ikkinchisi eski telefon bilan ustidan yozadi (lost update) - pastdagi test buni ko'rsatadi.
E4.2 Identity map: repozitoriy ichida get(42) har safar BIR XIL obyektni qaytaradi (`is` bilan tekshiriladi).
E4.3 AGGREGATION: repozitoriy mijozlarga havola ushlaydi (identity map), lekin lifetime test: mijoz repozitoriy
     bilan birga yo'qolmaydi (u bazada yashaydi va handler uni repo'dan keyin ham ushlab turishi mumkin).
E4.4 Ikki xil SERVER bir mijozni o'zgartirsa identity map yordam bermaydi (obyektlar turli jarayonlarda). Yechim -
     optimistic locking: har qatorda `version`; UPDATE ... WHERE id=? AND version=? va 0 qator yangilansa - konflikt,
     qayta o'qib qayta urinish.
"""
import pytest


class Customer:
    def __init__(self, customer_id, name, phone):
        self.customer_id, self.name, self.phone = customer_id, name, phone


class PlainCustomerRepository:
    """Asl (xato) variant: get() har safar yangi obyekt yasaydi."""

    def __init__(self, rows):
        self._rows = rows  # bazani almashtiradi: id -> dict

    def get(self, customer_id):
        row = self._rows[customer_id]
        return Customer(customer_id, row["name"], row["phone"])

    def save(self, customer):
        self._rows[customer.customer_id] = {"name": customer.name, "phone": customer.phone}


class CustomerRepository(PlainCustomerRepository):
    """Identity map bilan: bitta id -> bitta obyekt."""

    def __init__(self, rows):
        super().__init__(rows)
        self._identity_map: dict[int, Customer] = {}

    def get(self, customer_id):
        if customer_id not in self._identity_map:
            self._identity_map[customer_id] = super().get(customer_id)
        return self._identity_map[customer_id]


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
OLD, NEW = "+998901111111", "+998902222222"


def make_rows():
    return {42: {"name": "Ali", "phone": OLD}}


def test_e4_1_lost_update_with_plain_repository():
    rows = make_rows()
    repo = PlainCustomerRepository(rows)
    first, second = repo.get(42), repo.get(42)   # ikki ekran
    first.phone = NEW
    repo.save(first)
    repo.save(second)                            # eski telefon bilan ustidan yozdi
    assert rows[42]["phone"] == OLD              # o'zgarish yo'qoldi


def test_e4_2_identity_map_returns_the_same_object():
    repo = CustomerRepository(make_rows())
    assert repo.get(42) is repo.get(42)


def test_lost_update_cannot_happen_inside_one_repository():
    rows = make_rows()
    repo = CustomerRepository(rows)
    first, second = repo.get(42), repo.get(42)
    first.phone = NEW
    repo.save(first)
    repo.save(second)                            # second is first -> yangi telefon
    assert rows[42]["phone"] == NEW


def test_unknown_customer_raises_key_error():
    with pytest.raises(KeyError):
        CustomerRepository(make_rows()).get(999)


def test_each_repository_has_its_own_identity_map():
    rows = make_rows()
    assert CustomerRepository(rows).get(42) is not CustomerRepository(rows).get(42)


# --------------------------------------------------------------------------
# Done when:
#   [x] repo.get(42) is repo.get(42) -> True        -> test_e4_2_identity_map_returns_the_same_object
#   [x] bir repozitoriy ichida yo'qolgan yangilanish bo'lmaydi -> test_lost_update_cannot_happen_inside_one_repository
# --------------------------------------------------------------------------
