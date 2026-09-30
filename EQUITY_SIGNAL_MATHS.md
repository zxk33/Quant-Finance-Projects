# Mathematics: Cross-Sectional Equity Signals

This note gives the mathematics behind the equity-screening framework in
`equity_signal_research.py`.

## 1. Cross-sectional standardisation

For signal k, asset i and date t, the raw feature x is converted into a
cross-sectional z-score

[
z_{i,t}^{(k)} = rac{x_{i,t}^{(k)}-mu_t^{(k)}}{sigma_t^{(k)}}.
]

This makes signals with different units comparable inside the same date. A
direction coefficient d_k in {+1,-1} determines whether larger or smaller raw
values are preferred.

## 2. Composite score

With K signals,

[
s_{i,t} = rac{1}{K}sum_{k=1}^{K} d_k z_{i,t}^{(k)}.
]

The score is intentionally transparent: there is no fitted black-box model.

## 3. Market-neutral portfolio

Assets are ranked by s. The highest-scoring q fraction is long and the
lowest-scoring q fraction is short. With n_L longs and n_S shorts,

[
w_{i,t}=
egin{cases}
+0.5/n_L & i in L_t,\
-0.5/n_S & i in S_t,\
0 & 	ext{otherwise}.
end{cases}
]

Therefore gross exposure is 1 and net exposure is 0.

## 4. Turnover and transaction costs

Portfolio turnover is

[
T_t = sum_i |w_{i,t}-w_{i,t-1}|.
]

If the assumed one-way cost is c basis points, the cost-adjusted next-period
return is

[
r_{p,t+1} = sum_i w_{i,t}r_{i,t+1} - T_t c	imes10^{-4}.
]

## 5. Performance statistics

The implementation reports cumulative return, annualised Sharpe ratio, maximum
drawdown and average turnover. For daily data,

[
	ext{Sharpe} = sqrt{252},rac{ar r}{s_r}.
]

## 6. Timing discipline

Weights for date t use only features available at t; forward returns are
evaluated only after the weights are fixed. Fundamental features must be lagged
to their actual publication dates. Otherwise the test contains look-ahead bias.

This framework is a research tool, not evidence that any particular signal
produces persistent live-market alpha.
