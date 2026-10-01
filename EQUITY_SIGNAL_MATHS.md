# Mathematics: Equity Screening & Backtesting

The implementation in [equity_signal_research.py](equity_signal_research.py) is an educational framework. It does not claim to have discovered profitable real-market signals.

## 1. Standardise each feature

For asset \(i\), feature \(k\) and date \(t\), compute its cross-sectional z-score:

$$
z_{i,t}^{(k)}=\frac{x_{i,t}^{(k)}-\mu_t^{(k)}}{\sigma_t^{(k)}}.
$$

Here \(\mu_t^{(k)}\) and \(\sigma_t^{(k)}\) are the mean and standard deviation across eligible assets **on the same date**. This makes features measured in different units comparable.

## 2. Build a transparent score

For \(K\) features and chosen direction \(d_k\in\{-1,1\}\):

$$
s_{i,t}=\frac{1}{K}\sum_{k=1}^{K} d_k z_{i,t}^{(k)}.
$$

Rank assets by this score. There is no trained predictive model hidden in the score.

## 3. Construct an approximately market-neutral portfolio

Select the highest-scoring \(n_L\) assets for the long basket and the lowest-scoring \(n_S\) for the short basket. Equal weights within each basket give

$$
w_{i,t}=\begin{cases}
\frac{0.5}{n_L} & i\in L_t,\\
-\frac{0.5}{n_S} & i\in S_t,\\
0 & \text{otherwise}.
\end{cases}
$$

The portfolio has unit gross exposure and zero net dollar exposure by construction. Dollar neutrality does **not** guarantee beta neutrality.

## 4. Evaluate return after costs

If \(r_{i,t+1}\) is the *next-period* asset return and \(c\) is the assumed transaction cost in basis points:

$$
T_t=\sum_i |w_{i,t}-w_{i,t-1}|,
$$

$$
R_{t+1}=\sum_i w_{i,t}r_{i,t+1}-T_t\frac{c}{10{,}000}.
$$

Weights are determined before the forward return is applied.

## 5. Report risk alongside returns

For daily portfolio returns \(R_t\), the annualised sample Sharpe (assuming zero benchmark rate) is

$$
\widehat{SR}=\sqrt{252}\,\frac{\overline R}{s_R}.
$$

The code also computes cumulative return, drawdown and turnover.

## Limitations

Fundamental indicators require actual **publication-date lags**. Any real-data study must additionally control for survivorship bias, liquidity constraints, changing universes, borrowing costs, subperiod sensitivity and out-of-sample selection. The repository provides a testing framework, not independently validated alpha.
