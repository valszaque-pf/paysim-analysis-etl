with daily_transactions as (
    select
        simulation_day,
        type,
        COUNT(*) as transaction_count,
        COUNT(*) filter (
            where is_fraud
        ) as fraud_count,
        COALESCE(
            SUM(amount) filter (
                where is_fraud
            ),
            0
        ) as fraudulent_amount
    from paysim
    where type in ('TRANSFER', 'CASH_OUT')
    group by
        simulation_day,
        type
)
select
    simulation_day,
    type,
    transaction_count,
    fraud_count,
    fraudulent_amount,
    ROUND(
        100.0 * fraud_count
        / NULLIF(transaction_count, 0),
        4
    ) as fraud_rate_pct
from daily_transactions
order by
    simulation_day,
    type
