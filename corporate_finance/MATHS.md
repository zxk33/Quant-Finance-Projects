# Mathematics: Company Valuation

This note explains the mathematics used in the [valuation module](valuation.py). Supplied examples are **fictional practice inputs**, not proprietary investment research.

## 1. Unlevered free cash flow

$$
UFCF_t=EBIT_t(1-\tau)+D\&A_t-Capex_t-\Delta NWC_t,
$$

where \(\tau\) is the assumed cash tax rate.

## 2. Discounted cash flow

Discount forecast cash flow using weighted-average cost of capital:

$$
PV(UFCF_t)=\frac{UFCF_t}{(1+WACC)^t}.
$$

A constant-growth terminal value after year \(n\) is

$$
TV_n=\frac{UFCF_n(1+g)}{WACC-g}, \qquad g<WACC.
$$

Thus

$$
EV=\sum_{t=1}^{n}\frac{UFCF_t}{(1+WACC)^t}+
\frac{TV_n}{(1+WACC)^n}.
$$

The simplified enterprise-to-equity bridge is

$$
Equity\ Value=EV-Net\ Debt.
$$

Diluted per-share value is equity value divided by diluted shares outstanding.

## 3. Sensitivity analysis

Change both \(WACC\) and terminal growth \(g\) over a specified grid. Report the resulting valuation **range**, since small changes in long-run assumptions can materially change terminal value.

## 4. Peer multiples

For peer \(j\):

$$
M_j=\frac{EV_j}{EBITDA_j}.
$$

Apply a selected peer multiple to the target's EBITDA; bridge implied enterprise value to equity value using the target's net debt.

## 5. Acquisition earnings per share

The simplified standalone EPS calculation is

$$
EPS_A=\frac{NI_A}{Shares_A}.
$$

For an acquisition, pro-forma earnings combine the parties' earnings with stated financing, synergy and other transaction assumptions. Stock issued increases the diluted share count. The EPS comparison is

$$
Accretion/Dilution=\frac{EPS_{pro\ forma}}{EPS_A}-1.
$$

This educational module is not a full three-statement transaction model; results depend on the fictional inputs and selected assumptions.
