select 
    step,
    type,
    amount,
    hour_of_day,
    simulation_day
from paysim
where is_fraud
order by simulation_day
