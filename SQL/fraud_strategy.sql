select
    amount,
    oldbalance_orig
from paysim
where is_fraud
  and type = 'TRANSFER'
  and amount = 10000000
order by oldbalance_orig