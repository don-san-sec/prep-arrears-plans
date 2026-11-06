from datetime import date

from arrears.models import Payment
from arrears.payments import allocate


def test_payment_goes_to_the_bill_first() -> None:
    assert allocate(Payment(5000, date(2026, 10, 5), "bill"), 5000) == (5000, 0)


def test_remainder_reduces_arrears() -> None:
    assert allocate(Payment(7000, date(2026, 10, 5), "bill"), 5000) == (5000, 2000)


def test_part_payment_never_reaches_arrears() -> None:
    assert allocate(Payment(2500, date(2026, 10, 5), "slice"), 6000) == (2500, 0)


def test_slice_payment_counts_only_once_the_bill_is_clear() -> None:
    assert allocate(Payment(2500, date(2026, 10, 5), "slice"), 0) == (0, 2500)
