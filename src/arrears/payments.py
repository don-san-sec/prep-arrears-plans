"""Payment allocation for arrears customers (rule 1 of the arrears handbook)."""

from __future__ import annotations

from arrears.models import Payment


def allocate(payment: Payment, bill_outstanding: int) -> tuple[int, int]:
    """Split a payment between the current bill and arrears.

    Rule 1: any payment received is applied to the current bill first; only
    the remainder reduces arrears. A payment never counts toward the plan
    slice while the current bill is unpaid.
    """
    bill_paid = min(payment.amount_pence, bill_outstanding)
    arrears_paid = payment.amount_pence - bill_paid
    return bill_paid, arrears_paid