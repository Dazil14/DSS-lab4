"""
E1 - Someone changed the settings at runtime

E1.1 Settings - @dataclass(frozen=True): env, max_upload_mb (1..100), db_url.
E1.2 Qiymatlar __post_init__ da tekshiriladi, shuning uchun noto'g'ri konfiguratsiya dastur ishga tushishidayoq to'xtaydi.
E1.3 `settings.max_upload_mb = 500` -> dataclasses.FrozenInstanceError (u AttributeError'ning bolasi).
E1.4 Bitta handler uchun o'zgargan NUSXA: `dataclasses.replace(settings, max_upload_mb=...)`: umumiy obyekt tegilmaydi.
     Ha, replace() yangi obyektni konstruktor orqali yaratadi, ya'ni __post_init__ qayta ishlaydi - pastdagi test isboti.
"""
from dataclasses import FrozenInstanceError, dataclass, replace

import pytest

ALLOWED_ENVS = ("dev", "staging", "prod")


@dataclass(frozen=True)
class Settings:
    env: str
    max_upload_mb: int
    db_url: str

    def __post_init__(self):
        if self.env not in ALLOWED_ENVS:
            raise ValueError(f"env {ALLOWED_ENVS} dan biri bo'lishi kerak, berildi: {self.env!r}")
        if isinstance(self.max_upload_mb, bool) or not isinstance(self.max_upload_mb, int):
            raise TypeError("max_upload_mb int bo'lishi kerak")
        if not 1 <= self.max_upload_mb <= 100:
            raise ValueError("max_upload_mb 1..100 oralig'ida bo'lishi kerak")
        if not isinstance(self.db_url, str) or not self.db_url:
            raise ValueError("db_url bo'sh bo'lmagan str bo'lishi kerak")


def make_settings() -> Settings:
    return Settings(env="prod", max_upload_mb=20, db_url="postgresql://db.internal/app")


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
def test_changing_a_field_raises_error():
    settings = make_settings()
    with pytest.raises(FrozenInstanceError):
        settings.max_upload_mb = 500
    assert isinstance(FrozenInstanceError(), AttributeError)
    assert settings.max_upload_mb == 20


@pytest.mark.parametrize("env", ["production", "", "DEV"])
def test_wrong_env_fails_at_startup(env):
    with pytest.raises(ValueError):
        Settings(env=env, max_upload_mb=10, db_url="x")


@pytest.mark.parametrize("limit", [0, -5, 101, 500])
def test_wrong_limit_fails_at_startup(limit):
    with pytest.raises(ValueError):
        Settings(env="dev", max_upload_mb=limit, db_url="x")


@pytest.mark.parametrize("limit", [1, 100])
def test_limit_boundaries_are_allowed(limit):
    assert Settings(env="dev", max_upload_mb=limit, db_url="x").max_upload_mb == limit


def test_wrong_limit_type_fails():
    with pytest.raises(TypeError):
        Settings(env="dev", max_upload_mb="50", db_url="x")


def test_replace_returns_a_checked_copy_and_keeps_original():
    shared = make_settings()
    big = replace(shared, max_upload_mb=100)
    assert big.max_upload_mb == 100 and big is not shared
    assert shared.max_upload_mb == 20            # umumiy obyekt o'zgarmagan


def test_replace_runs_the_checks_again():
    shared = make_settings()
    with pytest.raises(ValueError):
        replace(shared, max_upload_mb=500)       # __post_init__ qayta ishladi
    with pytest.raises(ValueError):
        replace(shared, env="oops")


# --------------------------------------------------------------------------
# Done when:
#   [x] maydonni o'zgartirish xato beradi        -> test_changing_a_field_raises_error
#   [x] noto'g'ri env/limit start-up'da yiqiladi -> test_wrong_env_fails_at_startup, test_wrong_limit_fails_at_startup
#   [x] replace() tekshirilgan nusxa qaytaradi   -> test_replace_runs_the_checks_again
# --------------------------------------------------------------------------
