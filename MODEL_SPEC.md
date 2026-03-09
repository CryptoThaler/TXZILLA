# MODEL_SPEC.md

## Baseline formulas

### Monthly cash flow
monthly_cash_flow = estimated_rent - taxes_monthly - insurance_monthly - maintenance_monthly - hoa_monthly - vacancy_reserve_monthly - management_cost_monthly

### Annual NOI
annual_noi = monthly_cash_flow * 12

### Cap rate
cap_rate = annual_noi / acquisition_basis

### Investment score
investment_score =
0.30 * cash_flow_score +
0.25 * appreciation_score +
0.20 * market_growth_score +
0.15 * risk_inverse_score +
0.10 * liquidity_score

## Constraints
- deterministic
- explainable
- versioned
- scenario overlays separate from baseline
