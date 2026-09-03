# Market Making Under Uncertainty - Mathematical Notes

[Back to the portfolio](README.md) · [View the implementation](market_making.py) · [View the tests](test_market_making.py)

## 1. Objective

A market maker earns the spread when trades arrive but acquires inventory and adverse-selection risk. The experiment compares:

- **symmetric quoting**, where quotes remain centred on the current fair value; and
- **inventory-aware quoting**, where the quote centre moves against existing inventory, quote width grows with inventory and positions are capped.

The model asks whether simple inventory controls reduce the dispersion and downside frequency of terminal P&L under identical simulated order flow.

## 2. Fair-value dynamics

At each discrete time step, fair value follows

$$
F_{t+1}=F_t+\sigma\varepsilon_t+J_t,
$$

where $\varepsilon_t\sim\mathcal N(0,1)$, $\sigma$ is ordinary short-horizon volatility and $J_t$ is an occasional jump. In the code,

$$
J_t=I_tY_t,
\qquad I_t\sim\operatorname{Bernoulli}(0.012),
\qquad Y_t\sim\mathcal N(0,0.65^2).
$$

This mixture produces mostly small price changes with infrequent larger shocks.

## 3. Noisy informed order flow

The incoming trader observes a noisy value

$$
V_t=F_t+\alpha(F_{t+1}-F_t)+\eta_t,
$$

where $\alpha=0.85$ controls informedness and $\eta_t\sim\mathcal N(0,0.18^2)$ represents liquidity or valuation noise. A trader therefore tends to buy before an upward price move and sell before a downward move, creating adverse selection for the dealer.

## 4. Inventory-sensitive quotes

Let $q_t$ be dealer inventory, positive when the dealer is long. The reservation price is

$$
R_t=F_t-kq_t,
$$

and the half-width is

$$
w_t=h+\lambda|q_t|.
$$

The quoted prices are

$$
B_t=R_t-w_t,
\qquad A_t=R_t+w_t.
$$

For the risk-aware strategy, $h=0.10$, $k=0.035$, $\lambda=0.0025$ and $|q_t|\le 10$. If the dealer is long, $R_t$ shifts down: both quotes become more attractive to sellers of dealer inventory and less attractive to further buyers from the dealer. The widening term reduces trading intensity as the absolute position grows.

## 5. Trade, cash and inventory updates

If $V_t>A_t$, the trader buys one unit from the dealer:

$$
q_{t+1}=q_t-1,
\qquad X_{t+1}=X_t+A_t.
$$

If $V_t<B_t$, the trader sells one unit to the dealer:

$$
q_{t+1}=q_t+1,
\qquad X_{t+1}=X_t-B_t.
$$

Otherwise, neither cash $X_t$ nor inventory changes. Terminal marked-to-market P&L is

$$
\Pi_T=X_T+q_TF_T.
$$

This decomposes the outcome into realised trading cash and the fair-value mark of the remaining inventory.

## 6. Paired Monte Carlo design

Both strategies receive the same $\varepsilon_t$, $\eta_t$ and $J_t$ arrays in each trial. If $\Pi_i^{(S)}$ and $\Pi_i^{(R)}$ are symmetric and risk-aware P&Ls, the trial-level difference is

$$
D_i=\Pi_i^{(R)}-\Pi_i^{(S)}.
$$

Using common random numbers removes much of the variation caused merely by one strategy receiving an easier path. Formally,

$$
\operatorname{Var}(D)=\operatorname{Var}(\Pi^{(R)})+\operatorname{Var}(\Pi^{(S)})
-2\operatorname{Cov}(\Pi^{(R)},\Pi^{(S)}).
$$

A positive covariance therefore lowers the variance of the comparison.

## 7. Reported risk statistics

For $n$ simulated P&Ls $\Pi_1,\ldots,\Pi_n$, the code reports

$$
\bar\Pi=\frac1n\sum_{i=1}^n\Pi_i,
\qquad
s_\Pi=\sqrt{\frac1{n-1}\sum_{i=1}^n(\Pi_i-\bar\Pi)^2},
$$

$$
\widehat p_{\text{loss}}=\frac1n\sum_{i=1}^n\mathbf 1_{\{\Pi_i<0\}},
\qquad
\overline{q_{\max}}=\frac1n\sum_{i=1}^n\max_t|q_{i,t}|.
$$

The approximate 95% confidence interval for mean P&L is

$$
\bar\Pi\pm1.96\frac{s_\Pi}{\sqrt n}.
$$

With the default seed, 2,000 trials and 500 steps, the symmetric strategy has P&L volatility $30.14$, loss frequency $19.55\%$ and mean maximum inventory $21.32$. The inventory-aware strategy produces $4.13$, $0.20\%$ and $4.67$, respectively.

## 8. Interpretation and limitations

The experiment supports a narrow conclusion: under this synthetic order-flow model, inventory-sensitive quotes substantially reduce risk. It does **not** establish a profitable live strategy. The simulator omits latency, queue position, partial fills, fees, tick size, cross-asset hedging, calibration and strategic competitors. A natural extension would estimate parameters from limit-order-book data and evaluate out-of-sample performance after transaction costs.

## 9. Validation

The tests verify that the position limit is respected, seeded experiments are reproducible, and the risk-aware configuration reduces both average maximum inventory and P&L volatility for a fixed test experiment.
