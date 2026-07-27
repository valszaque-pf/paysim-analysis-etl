select 
    step,
    type,
    amount,
    hour_of_day,
    simulation_day
from paysim
where is_flagged_fraud
order by amount
