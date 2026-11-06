# Repayment-plan monitoring and escalation

Failed Direct Debit collections become arrears; the arrears team sets up
repayment plans, and ops wants the monitoring of those plans automated.

## Context

Brightwatt Energy is an app-first UK domestic energy supplier. About 180,000
customers pay a monthly bill by Direct Debit, and about 2.5% of monthly
collections fail. A failed collection becomes arrears, and the arrears team
sets up a repayment plan: for the next N months the customer pays their
normal monthly bill plus a fixed monthly plan slice. All amounts are stored
in whole pence.

Today the arrears team checks every plan by hand in a spreadsheet. Ops wants
that monitoring automated.

The ticket for this work is ARR-40:

> "Automate repayment-plan monitoring and escalation."

## The arrears handbook's plan rules

These come from the arrears team's collections handbook. Automated monitoring
must match it exactly, or customers get chased when they should not be — or
worse, vulnerable customers get automated letters.

1. **Payment allocation**: any payment received is applied to the **current
   bill first**; only the remainder reduces arrears. A payment **never**
   counts toward the plan slice while the current bill is unpaid.
2. A plan month is **missed** if the plan slice has not been received **in
   full** by the slice due date.
3. **Escalation**: a first miss sends an automated reminder. A **second
   consecutive** miss sends the final letter and moves the account to the
   collections queue. A caught-up month resets the consecutive-miss counter.
4. **Vulnerable customers** (priority register flag) must **never** receive
   automated escalation — no reminder, no final letter, no collections queue.
   Any missed slice for a vulnerable customer routes to the **specialist
   support team** instead.
5. A plan **completes** when every slice has been paid in full.

Worked examples from the handbook:

- A customer owes a 6,000p bill and a 2,500p slice is due this month. They
  pay 2,500p: all of it goes to the bill, the slice receives nothing, and the
  month is heading for a miss. Pay 8,500p instead and the bill is cleared and
  the slice is paid in full.
- A customer pays their 6,000p bill but only 2,000p of the 2,500p slice by
  the due date: the month is **missed** — the slice must arrive in full.
- January missed: automated reminder. February missed as well: final letter
  and the collections queue. February paid in full, then March missed:
  **reminder** — the caught-up month reset the counter.
- A missed month gets its automated reminder once. The monthly run does not
  chase the same missed slice again; that follow-up belongs to the arrears
  team.
- A priority-register customer misses a slice: the specialist support team
  gets the case. No automated letter ever goes out to them.
- The last of the N slices is paid in full: the plan is **complete**.

## How it works

```
src/arrears/
  models.py           Customer, Plan, Payment; plan status and actions
  payments.py         allocate(); any payment goes to the current bill first (rule 1)
tests/
```

Plan monitoring is not implemented yet. The arrears team assesses plans by
hand in a spreadsheet; this service owns the models and payment allocation.
The monthly collection run (not part of this service) records payments and
tags each one bill or slice.

## Running locally

```
uv sync
uv run pytest -q
```

## Your task

A colleague has opened a PR: https://github.com/don-san-sec/prep-arrears-plans/pull/1. You are the owner of this feature. Review the PR and decide whether to accept or reject it, and explain why.
