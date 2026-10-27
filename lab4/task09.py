"""
Task 9 - Splitting the god class

9.1  Metod -> ishlatadigan atributlar:
       add_student   -> students
       record_score  -> students, scores, submitted_at
       late_penalty  -> scores, deadlines, submitted_at
       final_grade   -> scores, weights (+ late_penalty orqali deadlines, submitted_at)
       letter        -> faqat final_grade natijasi
       export_csv    -> students (+ final_grade, letter natijalari)
       email_results -> students (+ natijalar), smtp_host
     Guruhlar: A) talabalar (add_student) | B) baho + muddat + topshirish vaqti (record_score, late_penalty) |
               C) vaznlar + B (final_grade, letter) | D) chiqarish/infratuzilma (export_csv, email_results).

9.2  "Event with data" = Submission: talaba bitta assessment'ga ish topshirdi (ball + vaqt) - Loan kabi, jarima
     qoidasi shu hodisaning ma'lumotiga tayanadi.
     CRC kartalar (har birida <= 4):
       Student        : 1. id va ismini biladi.                                   [Gradebook]
       Assessment     : 1. nomi, vazni (%), muddatini biladi.                     [Submission, GradeCalculator]
       Submission     : 1. student, assessment, ball, topshirish vaqtini biladi 2. necha kun kechikkanini sanaydi
                        3. kechikish jarimasini (%) hisoblaydi 4. jarimadan keyingi ballni beradi.   [Assessment]
       Gradebook      : 1. talabalarni saqlaydi 2. record_score: Submission yaratadi 3. talabaning Submission'larini
                        beradi.                                                   [Student, Submission, Assessment]
       GradeCalculator: 1. yakuniy bahoni hisoblaydi (vazn * jarimadan keyingi ball) 2. harfni (A-F) aniqlaydi.
                                                                                  [Submission, Assessment]
       CsvExporter    : 1. natijalarni CSV qatorlariga aylantiradi 2. faylga yozadi.   [Gradebook, GradeCalculator]
       ResultsMailer  : 1. xat matnini tuzadi 2. SMTP orqali yuboradi (smtp_host tashqaridan).
                                                                                  [Gradebook, GradeCalculator]

9.3  Kechikish jarimasini Submission hisoblaydi: unda ball va topshirish vaqti bor, muddatni Assessment'dan oladi.
     Yakuniy bahoni GradeCalculator hisoblaydi: unga talabaning barcha Submission'lari va Assessment vaznlari kerak.
     Faqat ishlatiladigan (saqlanmaydigan) klasslar - dependency: GradeCalculator, CsvExporter, ResultsMailer.
     Saqlanadigan bog'lanishlar: Gradebook -> Student (aggregation), Gradebook <>-> Submission (composition),
     Submission -> Assessment (association).
     Uch dasturchi parallel ishlaydi: (1) qoidalar: Submission/Assessment/GradeCalculator, (2) ma'lumot: Gradebook/
     Student, (3) chiqarish: CsvExporter/ResultsMailer - eksport va e-mail baho qoidalari bilan bir klassda emas.

9.4  Jarima qoidasi egasi - Submission (pastda). Qoida: har BOSHLANGAN kechikkan kun uchun -10%, eng ko'pi -50%.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest


@dataclass(frozen=True)
class Assessment:
    name: str
    weight: int          # foizda, masalan 30
    deadline: datetime


class Submission:
    PENALTY_PER_DAY = 10   # % har boshlangan kun uchun
    MAX_PENALTY = 50       # % ning eng ko'pi
    ONE_DAY = timedelta(days=1)

    def __init__(self, student_id: str, assessment: Assessment, score, submitted_at: datetime):
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise TypeError("score son bo'lishi kerak")
        if not 0 <= score <= 100:
            raise ValueError("score 0..100 oralig'ida bo'lishi kerak")
        self.student_id = student_id
        self.assessment = assessment
        self.score = score
        self.submitted_at = submitted_at

    def days_late(self) -> int:
        """Boshlangan kechikkan kunlar soni (muddatning o'zida topshirilsa - 0)."""
        late = self.submitted_at - self.assessment.deadline
        if late <= timedelta(0):
            return 0
        full_days, rest = divmod(late, self.ONE_DAY)
        return full_days + (1 if rest else 0)  # 1 daqiqa ham "boshlangan kun"

    def penalty_percent(self) -> int:
        return min(self.days_late() * self.PENALTY_PER_DAY, self.MAX_PENALTY)

    def penalized_score(self):
        return self.score * (100 - self.penalty_percent()) / 100


# --------------------------------------------------------------------------
# Testlar
# --------------------------------------------------------------------------
DEADLINE = datetime(2026, 11, 10, 23, 59)
ASSESSMENT = Assessment("lab4", 20, DEADLINE)


def submit(delta: timedelta, score=80) -> Submission:
    return Submission("U2310045", ASSESSMENT, score, DEADLINE + delta)


def test_on_time_has_no_penalty():
    s = submit(timedelta(hours=-3))
    assert (s.days_late(), s.penalty_percent(), s.penalized_score()) == (0, 0, 80)


def test_exactly_at_deadline_is_not_late():
    assert submit(timedelta(0)).penalty_percent() == 0


def test_one_minute_late_costs_one_started_day():
    s = submit(timedelta(minutes=1))
    assert (s.days_late(), s.penalty_percent(), s.penalized_score()) == (1, 10, 72)


def test_one_day_and_one_minute_late_costs_two_started_days():
    s = submit(timedelta(days=1, minutes=1))
    assert (s.days_late(), s.penalty_percent(), s.penalized_score()) == (2, 20, 64)


def test_six_days_late_is_capped_at_fifty_percent():
    s = submit(timedelta(days=6))
    assert (s.days_late(), s.penalty_percent(), s.penalized_score()) == (6, 50, 40)


@pytest.mark.parametrize(
    "delta, expected",
    [
        (timedelta(days=1), 10),                 # to'liq 1 kun = 1 kun
        (timedelta(days=5), 50),                 # chegara
        (timedelta(days=5, minutes=1), 50),      # 6 kun bo'lardi, lekin cheklov
    ],
)
def test_penalty_boundaries(delta, expected):
    assert submit(delta).penalty_percent() == expected


@pytest.mark.parametrize("bad", [-1, 101])
def test_score_out_of_range_is_rejected(bad):
    with pytest.raises(ValueError):
        submit(timedelta(0), score=bad)


# --------------------------------------------------------------------------
# Done when:
#   [x] hech bir yangi klassda 4 tadan ortiq mas'uliyat yo'q (9.2 kartalari)
#   [x] to'rtta jarima testi o'tadi (on time / 1 daqiqa / 1 kun 1 daqiqa / 6 kun)
#   [x] eksport va e-mail baho qoidalaridan alohida klasslarda (CsvExporter, ResultsMailer)
# --------------------------------------------------------------------------
