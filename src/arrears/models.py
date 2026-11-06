"""Customer, repayment-plan, and payment models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Literal


class PlanStatus(StrEnum):
    """Where a repayment plan stands."""

    ACTIVE = "ACTIVE"
    BROKEN = "BROKEN"
    COMPLETE = "COMPLETE"


class PlanAction(StrEnum):
    """What the monthly monitoring run tells ops to do about a plan."""

    NONE = "NONE"
    REMINDER = "REMINDER"
    FINAL_LETTER = "FINAL_LETTER"
    TO_COLLECTIONS = "TO_COLLECTIONS"
    SUPPORT_TEAM = "SUPPORT_TEAM"


@dataclass
class Customer:
    """A Brightwatt Energy customer.

    vulnerable is the priority register flag: customers on it must never
    receive automated escalation (arrears handbook, rule 4).
    """

    customer_id: str
    vulnerable: bool = False


@dataclass
class Plan:
    """A repayment plan: the monthly bill plus a fixed slice for N months.

    slice_pence is the fixed monthly amount on top of the bill and
    months_total is how many slices the plan runs for. All amounts are
    whole pence.
    """

    customer_id: str
    slice_pence: int
    months_total: int
    slices_paid: int = 0
    consecutive_misses: int = 0
    status: PlanStatus = PlanStatus.ACTIVE


@dataclass
class Payment:
    """A payment received from a customer, in whole pence.

    paid_toward is the ledger's tag for where the payment was intended to
    go: the current bill, or the plan slice.
    """

    amount_pence: int
    received_on: date
    paid_toward: Literal["bill", "slice"]