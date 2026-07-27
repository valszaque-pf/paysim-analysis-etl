with transfers as (
    select
        type,
        name_dest,
        step,
        amount
    from paysim
    where is_fraud
        and type = 'TRANSFER'
),
cash_outs as (
    select
        type,
        name_orig,
        step,
        amount
    from paysim
    where is_fraud
        and type = 'CASH_OUT'
)
select
    t.name_dest as transfer_name,
    c.name_orig as cashout_name,
    t.amount as transfer_amount,
    c.amount as cashout_amount,
    c.step as cashout_step,
    t.step as transfer_step
from transfers as t
inner join cash_outs as c
    on t.name_dest = c.name_orig
    and c.step = t.step
order by cashout_step
