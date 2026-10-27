"""
E2 - API tokens in the error tracker

E2.1 @dataclass generatsiya qilgan repr to'rtala maydonni ham chiqaradi: user_id, email (shaxsiy ma'lumot),
     password_hash (oflayn buzish mumkin) va api_token (to'liq sir - u bilan foydalanuvchi nomidan kirib bo'ladi).
E2.2 password_hash repr'dan butunlay olib tashlanadi, api_token faqat oxirgi 4 belgi bilan: tok_****9f2a.
E2.3 Ha, farq qilishi kerak: __str__ - odamlar uchun (UI): faqat email; __repr__ - dasturchilar uchun (log): id, email
     va maskalangan token. Ikkalasida ham sir yo'q.
E2.4 `field(repr=False)` maydonni == dan OLIB TASHLAMAYDI (taqqoslash alohida `compare` bayrog'i bilan boshqariladi).
     User uchun bu muhim: aks holda token almashgan (rotation) o'sha foydalanuvchi "boshqa" bo'lib qoladi va sirlar
     taqqoslanadi - shuning uchun sirlarda compare=False ham qo'yildi.
"""
from dataclasses import dataclass, field


def mask_token(token: str) -> str:
    return f"tok_****{token[-4:]}"


@dataclass(repr=False)
class User:
    user_id: int
    email: str
    password_hash: str = field(repr=False, compare=False)
    api_token: str = field(repr=False, compare=False)

    def __repr__(self) -> str:  # dasturchilar / log uchun
        return f"User(user_id={self.user_id!r}, email={self.email!r}, api_token={mask_token(self.api_token)!r})"

    def __str__(self) -> str:  # odamlar / UI uchun
        return self.email


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
def make_user(**overrides) -> User:
    data = dict(user_id=7, email="ali@example.uz", password_hash="pbkdf2$SECRETSALT$SECRETHASH",
                api_token="tok_live_abc9f2a")
    data.update(overrides)
    return User(**data)


def test_default_dataclass_repr_leaks_everything():
    @dataclass
    class LeakyUser:
        user_id: int
        email: str
        password_hash: str
        api_token: str

    text = repr(LeakyUser(7, "ali@example.uz", "pbkdf2$SECRETSALT$SECRETHASH", "tok_live_abc9f2a"))
    for leaked in ("ali@example.uz", "SECRETHASH", "tok_live_abc9f2a"):
        assert leaked in text


def test_repr_hides_password_hash_completely():
    text = repr(make_user())
    assert "password_hash" not in text and "SECRET" not in text and "pbkdf2" not in text


def test_repr_masks_token_and_shows_only_last_four():
    text = repr(make_user())
    assert "tok_****9f2a" in text
    assert "live_abc" not in text and "tok_live_abc9f2a" not in text


def test_str_has_no_secrets_and_differs_from_repr():
    user = make_user()
    assert str(user) == "ali@example.uz"
    assert str(user) != repr(user)
    for secret in ("SECRET", "tok_live", "9f2a"):
        assert secret not in str(user)


def test_repr_false_alone_does_not_remove_field_from_eq():
    @dataclass
    class Demo:
        a: int
        secret: str = field(repr=False)

    assert Demo(1, "x") != Demo(1, "y")      # repr=False == ga ta'sir qilmaydi
    assert "secret" not in repr(Demo(1, "x"))


def test_user_equality_ignores_rotating_secrets():
    assert make_user() == make_user(api_token="tok_live_new1111", password_hash="other")
    assert make_user() != make_user(user_id=8)


# --------------------------------------------------------------------------
# Done when:
#   [x] repr() va str() da sir yo'q -> test_repr_hides_password_hash_completely, test_str_has_no_secrets_and_differs_from_repr
#   [x] maskalangan token faqat oxirgi 4 belgini ko'rsatadi -> test_repr_masks_token_and_shows_only_last_four
# --------------------------------------------------------------------------
