select 
    transfers,
    cash_outs,
    COUNT(*) as quantity
from (
    select 
        amount, 
        step,
        SUM(case when type = 'TRANSFER' then 1 else 0 end) as transfers,
        SUM(case when type = 'CASH_OUT' then 1 else 0 end) as cash_outs
    from paysim
    where is_fraud
    group by amount, step
) as cardinalities
group by transfers, cash_outs
order by quantity desc
