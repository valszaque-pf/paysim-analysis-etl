select 
    amount, 
    step,
    SUM(case when type = 'TRANSFER' then 1 else 0 end) as transfers,
    SUM(case when type = 'CASH_OUT' then 1 else 0 end) as cash_outs,
    COUNT(*) as total_freq
from paysim
where is_fraud
group by 
    amount, 
    step
having SUM(case when type = 'TRANSFER' then 1 else 0 end) > 1
or SUM(case when type = 'CASH_OUT' then 1 else 0 end) > 1
order by total_freq desc