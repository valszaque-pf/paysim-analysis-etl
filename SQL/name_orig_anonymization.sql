select 
    name_orig, 
    count(*) as times
from paysim
group by name_orig