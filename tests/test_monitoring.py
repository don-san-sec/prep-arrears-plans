from datetime import date

from arrears.models import Customer, Payment, Plan, PlanAction, PlanStatus
from arrears.monitoring import assess_plan


def test_on_track_month_needs_no_action() -> None:
    plan = Plan("cus_0001", slice_pence=2500, months_total=6)
    customer = Customer("cus_0001", vulnerable=False)

    action = assess_plan(
        plan,
        customer,
        bill_payments=[Payment(6000, date(2026, 10, 5), "bill")],
        slice_payments=[Payment(2500, date(2026, 10, 5), "slice")],
        slice_due_on=date(2026, 10, 31),
        as_of=date(2026, 11, 15),
    )

    assert action is PlanAction.NONE
    assert plan.slices_paid == 1
    assert plan.consecutive_misses == 0
    assert plan.status is PlanStatus.ACTIVE


def test_paying_the_last_slice_completes_the_plan() -> None:
    plan = Plan("cus_0001", slice_pence=2500, months_total=3, slices_paid=2)
    customer = Customer("cus_0001", vulnerable=False)

    action = assess_plan(
        plan,
        customer,
        bill_payments=[Payment(6000, date(2026, 10, 5), "bill")],
        slice_payments=[Payment(2500, date(2026, 10, 5), "slice")],
        slice_due_on=date(2026, 10, 31),
        as_of=date(2026, 11, 15),
    )

    assert action is PlanAction.NONE
    assert plan.slices_paid == 3
    assert plan.status is PlanStatus.COMPLETE


def test_first_miss_sends_a_reminder() -> None:
    plan = Plan("cus_0001", slice_pence=2500, months_total=6)
    customer = Customer("cus_0001", vulnerable=False)

    action = assess_plan(
        plan,
        customer,
        bill_payments=[],
        slice_payments=[],
        slice_due_on=date(2026, 10, 31),
        as_of=date(2026, 11, 15),
    )

    assert action is PlanAction.REMINDER
    assert plan.consecutive_misses == 1
    assert plan.status is PlanStatus.ACTIVE
