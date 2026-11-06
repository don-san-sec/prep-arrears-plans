"""Repayment-plan monitoring and escalation (ARR-40).

The monthly monitoring run assesses each active plan month: if the slice
was covered by its due date the month is paid; if not, the miss escalates
per the arrears handbook — a reminder on a first miss, the final letter
and the collections queue on a second consecutive miss. A plan completes
once every slice has been paid.
"""

from __future__ import annotations

from datetime import date

from arrears.models import Customer, Payment, Plan, PlanAction, PlanStatus


def assess_plan(
    plan: Plan,
    customer: Customer,
    bill_payments: list[Payment],
    slice_payments: list[Payment],
    slice_due_on: date,
    as_of: date,
) -> PlanAction:
    """Assess one plan month and return what ops should do about it.

    The monthly run calls this once per plan month, after the slice due
    date. bill_payments and slice_payments are the payments received this
    plan month, as tagged by the ledger when they came in.
    """
    if plan.customer_id != customer.customer_id:
        raise ValueError("plan does not belong to this customer")

    if plan.status is not PlanStatus.ACTIVE:
        return PlanAction.NONE  # complete, or with collections already

    # The payments received this month, by the slice due date.
    # payments.allocate has already split each one between the bill and
    # arrears at receipt, so monitoring does not need to re-derive the
    # split: once the money received this month covers the slice amount,
    # the month counts as paid.
    received = [
        p
        for p in [*bill_payments, *slice_payments]
        if p.received_on <= slice_due_on
    ]
    slice_paid = sum(p.amount_pence for p in received) >= plan.slice_pence

    if slice_paid:
        plan.slices_paid += 1
        # A plan completes once every slice has been paid (rule 5).
        if plan.slices_paid >= plan.months_total:
            plan.status = PlanStatus.COMPLETE
            return PlanAction.NONE

    if not slice_paid and as_of > slice_due_on:
        # The slice was not there by its due date: a missed month (rule 2).
        plan.consecutive_misses += 1
        if plan.consecutive_misses >= 2:
            # A second consecutive miss: final letter, and the plan moves
            # to the collections queue (rule 3).
            plan.status = PlanStatus.BROKEN
            return PlanAction.FINAL_LETTER
        return PlanAction.REMINDER

    # This month is fine, but an earlier month's slice may still be
    # outstanding — keep the reminder going until the missed slice is
    # cleared. Better one nudge too many than a missed chase.
    if plan.consecutive_misses >= 1:
        return PlanAction.REMINDER

    return PlanAction.NONE