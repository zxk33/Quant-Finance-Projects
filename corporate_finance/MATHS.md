# Mathematics: Corporate Valuation

This note summarises the mathematics used by the corporate valuation module.

## 1. Unlevered free cash flow

[
UFCF_t = EBIT_t(1-	au) + D&A_t - Capex_t - Delta NWC_t.
]

The model forecasts operating results for five years and discounts unlevered
cash flow at WACC.

## 2. Discounted cash flow

[
PV(UFCF_t)=rac{UFCF_t}{(1+WACC)^t}.
]

Terminal value uses the Gordon growth model:

[
TV_n = rac{UFCF_n(1+g)}{WACC-g},
qquad g < WACC.
]

Enterprise value is

[
EV = sum_{t=1}^{n}rac{UFCF_t}{(1+WACC)^t}
     + rac{TV_n}{(1+WACC)^n}.
]

Equity value follows from the enterprise-value bridge:

[
Equity Value = EV - Net Debt.
]

Per-share value is equity value divided by diluted shares outstanding.

## 3. Sensitivity analysis

The model evaluates a grid of WACC and terminal-growth assumptions. This matters
because terminal value can represent a large fraction of DCF enterprise value.

## 4. Trading comparables

For a peer j,

[
EV/EBITDA_j = rac{EV_j}{EBITDA_j}.
]

The peer median multiple is applied to target EBITDA to obtain an implied
enterprise value, which is then bridged to equity value.

## 5. Acquisition EPS

Standalone EPS is

[
EPS_A = rac{Net Income_A}{Shares_A}.
]

For a transaction funded with cash, debt and stock, pro-forma earnings adjust
for target earnings, after-tax interest, foregone cash interest and synergies.
New shares equal stock consideration divided by the acquirer share price.

[
Accretion/Dilution = rac{EPS_{proforma}}{EPS_A}-1.
]

The model is intentionally simplified and does not claim to be a full
three-statement merger model.
