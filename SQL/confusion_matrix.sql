with transaction_groups as (
    select
        step,
        amount,
        COUNT(*) filter (
            where type = 'TRANSFER'
        ) as transfer_count,
        COUNT(*) filter (
            where type = 'CASH_OUT'
        ) as cashout_count
    from paysim
    where type in ('TRANSFER', 'CASH_OUT')
    group by
        step,
        amount
),
scored_transactions as (
    select
        p.*,
        g.transfer_count,
        g.cashout_count,
        (
            g.transfer_count = 1
            and g.cashout_count = 1
        ) as pair_rule
    from paysim as p
    left join transaction_groups as g
        on p.step = g.step
       and p.amount = g.amount
),
rules as (
    select
        scored.*,
        evaluated.rule_name,
        evaluated.predicted_fraud
    from scored_transactions as scored
    cross join lateral (
        values
            (
                'original_rule',
                scored.is_flagged_fraud
            ),
            (
                'new_rule',
                scored.type in ('TRANSFER', 'CASH_OUT')
                and scored.pair_rule
            )
    )
    as evaluated(
        rule_name,
        predicted_fraud
    )
),
confusion_matrix as (
    select
        rule_name,
        COUNT(*) filter (
            where predicted_fraud
        ) as generated_alerts,
        COUNT(*) filter (
            where predicted_fraud
              and is_fraud
        ) as true_positives,
        COUNT(*) filter (
            where predicted_fraud
              and not is_fraud
        ) as false_positives,
        COUNT(*) filter (
            where not predicted_fraud
              and is_fraud
        ) as false_negatives,
        COUNT(*) filter (
            where not predicted_fraud
              and not is_fraud
        ) as true_negatives
    from rules
    group by
        rule_name
),
metrics as (
    select
        *,
        true_positives::numeric
        / nullif(
            true_positives + false_positives,
            0
        ) as precision,
        true_positives::numeric
        / nullif(
            true_positives + false_negatives,
            0
        ) as recall,
        true_negatives::numeric
        / nullif(
            true_negatives + false_positives,
            0
        ) as specificity
    from confusion_matrix
)
select
    rule_name,
    generated_alerts,
    true_positives,
    false_positives,
    false_negatives,
    true_negatives,
    ROUND(
        100 * precision,
        4
    ) as precision_pct,
    ROUND(
        100 * recall,
        4
    ) as recall_pct,
    ROUND(
        100 * specificity,
        4
    ) as specificity_pct,
    ROUND(
        100
        * (
            2 * precision * recall
            / NULLIF(precision + recall, 0)
        ),
        4
    ) as f1_score_pct
from metrics
order by
    case rule_name
        when 'original_rule' then 1
        when 'new_rule' then 2
    end
