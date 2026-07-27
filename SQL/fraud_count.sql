select 
    is_flagged_fraud,
    is_fraud,
    COUNT(*) AS count
from paysim
group by
    is_flagged_fraud,
    is_fraud