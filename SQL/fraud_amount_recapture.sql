with transaction_groups as (
    select
        step,
        amount,
        COUNT(*) filter (where type = 'TRANSFER') as transfer_count,
        COUNT(*) filter (where type = 'CASH_OUT') as cashout_count
    from paysim
    where type in ('TRANSFER', 'CASH_OUT')
    group by
        step,
        amount
),
flagged_transactions as (
    select
        p.amount,
        p.is_fraud,
        p.is_flagged_fraud,
        (g.transfer_count = 1 and g.cashout_count = 1) as new_detection_rule
    from paysim as p
    inner join transaction_groups as g
        on p.step = g.step
       and p.amount = g.amount
    where p.type in ('TRANSFER', 'CASH_OUT')
)
select
    SUM(amount) filter (where is_fraud) as total_fraud_amount,
    SUM(amount) filter (where is_fraud and is_flagged_fraud) as old_rule_recaptured_amount,
    SUM(amount) filter (where is_fraud and new_detection_rule) as new_rule_recaptured_amount,
    ROUND(
        100.0 * SUM(amount) filter (where is_fraud and is_flagged_fraud)
        / NULLIF(SUM(amount) filter (where is_fraud), 0),
        2
    ) as old_rule_recapture_pct,
    ROUND(
        100.0 * SUM(amount) filter (where is_fraud and new_detection_rule)
        / NULLIF(SUM(amount) filter (where is_fraud), 0),
        2
    ) as new_rule_recapture_pct
from flagged_transactions