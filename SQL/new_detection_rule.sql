with transaction_groups as (
    select
        step,
        amount,
        COUNT(*) filter (
            where type = 'TRANSFER'
        ) as transfer_count,
        COUNT(*) filter (
            where type = 'CASH_OUT'
        ) as cashout_count
    from paysim
    where type in ('TRANSFER', 'CASH_OUT')
    group by
        step,
        amount
),
detected_transactions as (
    select
        p.step,
        p.simulation_day,
        p.hour_of_day,
        p.type,
        p.amount,
        p.name_orig,
        p.name_dest,
        p.oldbalance_orig,
        p.newbalance_orig,
        p.oldbalance_dest,
        p.newbalance_dest,
        p.is_fraud,
        p.is_flagged_fraud,
        g.transfer_count,
        g.cashout_count,
        true as new_detection_rule
    from paysim as p
    inner join transaction_groups as g
        on p.step = g.step
       and p.amount = g.amount
    where p.type in ('TRANSFER', 'CASH_OUT')
      and g.transfer_count = 1
      and g.cashout_count = 1
)
select
    is_fraud,
    is_flagged_fraud,
    new_detection_rule
from detected_transactions