# Corporate valuation and acquisition scenarios

A reproducible Python case study linking operating assumptions to enterprise
value, equity value and acquisition EPS. **Every company and financial input in
the included example is fictional.** This is model-building practice, not
company research or a recommendation about a security.

```bash
python -m corporate_finance.valuation corporate_finance/example.json
python -m pytest corporate_finance/test_valuation.py -q
```

## Models

1. **Five-year DCF:** forecast revenue and EBIT, tax positive operating profits,
   add depreciation, subtract capex and changes in working capital. Discount
   unlevered free cash flow at WACC using end-year cash flows. Calculate a Gordon
   growth terminal value, subtract net debt and divide by diluted shares.
2. **Scenarios and sensitivity:** bear/base/bull operating cases and a 5-by-5
   WACC/terminal-growth matrix. Report the share of EV represented by terminal
   value so the reader can see how much rests on distant assumptions.
3. **Trading comparables:** calculate EV/EBITDA for each peer, exclude peers with
   nonpositive or nonfinite EV/EBITDA inputs, and apply the peer median to target
   EBITDA. Show the EV-to-equity bridge explicitly.
4. **Acquisition EPS:** split equity purchase consideration between cash, new
   debt and new shares; include after-tax debt interest, foregone cash interest
   and operating synergies. Compare pro forma EPS with standalone EPS.

## Equations and conventions

`UFCF = EBIT - cash tax + D&A - capex - change in NWC`  
`TV = final UFCF * (1 + g) / (WACC - g)`  
`Equity value = enterprise value - net debt`  
`New shares = stock consideration / acquirer share price`  
`Accretion = pro forma EPS / standalone EPS - 1`

Rates are decimals. The example uses GBP millions for financial amounts and
millions of shares, so per-share outputs are GBP. Net debt can be negative.
Cash taxes have a zero floor; no tax losses are carried forward. Terminal
cash flow grows the final forecast UFCF as a shortcut, rather than modelling
steady-state reinvestment and return on capital separately.

## What the tests establish

A flat-cash-flow DCF equals an independently calculated perpetuity. Other tests
check the working-capital bridge, debt subtraction, WACC sensitivity, invalid
inputs and loss-making peer exclusion. An all-stock acquisition at equal P/E
is EPS-neutral; another case verifies interest and synergy arithmetic by hand.

## Interpretation and limits

The base DCF and comparables need not agree: the DCF reflects selected growth
and reinvestment assumptions, while the multiples reflect an invented peer
set. EPS accretion does not establish value creation. The acquisition model
does not include purchase-price accounting, amortisation of acquired
intangibles, fees, refinancing target debt, integration costs, changing share
prices or partial-year timing. It is not a full merger or three-statement model.

Review `example.json` and `example_output.json` together to audit every input
and output. Change assumptions before interpreting a result.

## Development provenance

Implemented and tested with Codex assistance. The fictional case, source and
tests are included so the calculations can be reproduced and extended.
