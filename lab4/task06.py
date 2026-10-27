"""
Task 6 - Duplicates after the nightly import

6.1  __eq__ va __hash__ yozilmasa, ikkalasi ham `object`dan meros: `==` obyektlar BIR XIL obyektmi (`is`) ekanini
     tekshiradi, hash() esa obyekt manziliga (id) asoslanadi. Shuning uchun bir xil ma'lumotli ikkita Student turlicha.
6.2  Klass faqat __eq__ yozsa, Python avtomatik `__hash__ = None` qo'yadi: obyekt hashable emas va `set.add` TypeError
     ("unhashable type") beradi.
6.3  "Bir xil student" = bir xil student_id (registrar bergan o'zgarmas identifikator). SE-31 -> SE-32 o'tgan talaba
     BIR XIL talaba (shaxs o'sha), shuning uchun group va full_name taqqoslashga kirmaydi. __eq__ va __hash__
     faqat student_id'dan foydalanadi; student_id read-only (hash o'zgarmasligi uchun).
6.4  Hash group'ga bog'liq bo'lsa (pastdagi test): set'ga qo'shgach s.group o'zgarsa, hash o'zgaradi va `s in seen`
     False bo'ladi - obyekt set'ning noto'g'ri "qutisi"da qolib ketadi.
6.5  @dataclass(frozen=True) eq/hash'ni BARCHA maydonlardan yasaydi (student_id, full_name, group): group o'zgargan
     talaba "boshqa" talaba bo'lib qoladi (yana dublikat), frozen esa group'ni o'zgartirishga ham yo'l qo'ymaydi,
     holbuki talaba o'zgaruvchan holatli entity.
6.6  __repr__ faqat student_id va group'ni ko'rsatadi (log'ga ism chiqmaydi).
"""
import pytest


class Student:
    def __init__(self, student_id, full_name, group):
        self._student_id = student_id  # identifikator o'zgarmaydi
        self.full_name = full_name
        self.group = group

    @property
    def student_id(self):
        return self._student_id

    def __eq__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self._student_id == other._student_id

    def __hash__(self):
        return hash(self._student_id)  # __eq__ bilan bir xil maydon

    def __repr__(self):
        return f"Student(student_id={self.student_id!r}, group={self.group!r})"


def import_students(rows):
    seen = set()
    for row in rows:
        seen.add(Student(*row))
    return seen


# Eslatma: set eski obyektni saqlaydi, shuning uchun yangi group yo'qolishi mumkin - haqiqiy jobda
# dict[student_id] ishlatib group'ni yangilash kerak. Bu vazifaning chegarasidan tashqarida.


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
ROWS = [("U2310045", "Ali Valiyev", "SE-31"), ("U2310045", "Ali Valiyev", "SE-31")]


def test_loop_gives_one_student():
    assert len(import_students(ROWS)) == 1


def test_moved_student_is_still_the_same_student():
    rows = ROWS[:1] + [("U2310045", "Ali Valiyev", "SE-32")]
    assert len(import_students(rows)) == 1


def test_student_is_found_after_group_change():
    s = Student("U2310045", "Ali Valiyev", "SE-31")
    seen = {s}
    s.group = "SE-32"
    assert s in seen


def test_equal_objects_have_equal_hashes():
    a = Student("U1", "Ali", "SE-31")
    b = Student("U1", "Ali Valiyev", "SE-32")
    assert a == b and hash(a) == hash(b)
    assert a != Student("U2", "Ali", "SE-31")


def test_comparison_with_other_types_is_false():
    assert Student("U1", "Ali", "SE-31") != "U1"


def test_student_id_is_read_only():
    s = Student("U1", "Ali", "SE-31")
    with pytest.raises(AttributeError):
        s.student_id = "U2"


def test_repr_matches_the_log_format():
    s = Student("U2310045", "Ali Valiyev", "SE-31")
    assert repr(s) == "Student(student_id='U2310045', group='SE-31')"


def test_6_1_default_eq_and_hash_are_identity_based():
    class Plain:
        def __init__(self, x):
            self.x = x

    assert Plain(1) != Plain(1) and hash(Plain(1)) != hash(Plain(1))


def test_6_2_only_eq_makes_class_unhashable():
    class OnlyEq:
        def __eq__(self, other):
            return True

    with pytest.raises(TypeError, match="unhashable"):
        {OnlyEq()}


def test_6_4_hash_that_depends_on_group_loses_the_student():
    class BadHashStudent(Student):
        def __hash__(self):
            return hash((self.student_id, self.group))  # o'zgaruvchan maydon!

    s = BadHashStudent("U2310045", "Ali Valiyev", "SE-31")   # 1
    seen = {s}                                               # 2
    s.group = "SE-32"                                        # 3
    assert (s in seen) is False                              # 4


def test_6_5_frozen_dataclass_compares_all_fields():
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class FrozenStudent:
        student_id: str
        full_name: str
        group: str

    old = FrozenStudent("U1", "Ali", "SE-31")
    moved = FrozenStudent("U1", "Ali", "SE-32")
    assert old != moved and len({old, moved}) == 2   # yana dublikat


if __name__ == "__main__":
    print(len(import_students(ROWS)))  # 1


# --------------------------------------------------------------------------
# Done when:
#   [x] sikl 1 ni chiqaradi                         -> test_loop_gives_one_student (yoki: python task06.py)
#   [x] group o'zgargach student set'da topiladi    -> test_student_is_found_after_group_change
#   [x] teng obyektlarning hash'i teng              -> test_equal_objects_have_equal_hashes
# --------------------------------------------------------------------------
