select 
    MAX(case when is_fraud then amount else 0 end) as max_fraud_amount,
    MAX(case when not is_fraud then amount else 0 end) as max_non_fraud_amount
from paysim
