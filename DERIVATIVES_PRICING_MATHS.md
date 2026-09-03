# Monte Carlo Derivatives Pricing - Mathematical Notes

[Back to the portfolio](README.md) · [View the implementation](derivatives_pricing.py) · [View the tests](test_derivatives_pricing.py)

## 1. Risk-neutral model

Under the risk-neutral measure $\mathbb Q$, a non-dividend-paying asset is modelled by geometric Brownian motion:

$$
dS_t=rS_t\,dt+\sigma S_t\,dW_t,
$$

where $r$ is the continuously compounded risk-free rate and $\sigma$ is volatility. Applying Itô's lemma to $\log S_t$ gives

$$
d\log S_t=\left(r-\frac12\sigma^2\right)dt+\sigma\,dW_t.
$$

Integrating from $0$ to $T$ produces the exact terminal distribution

$$
S_T=S_0\exp\left[\left(r-\frac12\sigma^2\right)T+\sigma\sqrt T\,Z\right],
\qquad Z\sim\mathcal N(0,1).
$$

The code samples this expression directly, so there is no time-discretisation error for a European payoff.

## 2. Risk-neutral valuation

For strike $K$, the call and put payoffs are

$$
H_{\text{call}}=(S_T-K)^+,
\qquad
H_{\text{put}}=(K-S_T)^+,
$$

where $x^+=\max(x,0)$. No-arbitrage pricing gives

$$
V_0=e^{-rT}\mathbb E^{\mathbb Q}[H].
$$

Given $N$ independent discounted payoffs $Y_i=e^{-rT}H_i$, the Monte Carlo estimator is

$$
\widehat V_N=\frac1N\sum_{i=1}^NY_i.
$$

It is unbiased for the model price when the terminal samples are generated correctly.

## 3. Sampling uncertainty

The sample variance and standard error are

$$
s_Y^2=\frac1{N-1}\sum_{i=1}^N(Y_i-\widehat V_N)^2,
\qquad
\operatorname{SE}(\widehat V_N)=\frac{s_Y}{\sqrt N}.
$$

The reported approximate 95% confidence interval is

$$
\widehat V_N\pm1.96\operatorname{SE}(\widehat V_N).
$$

Monte Carlo error converges at order $N^{-1/2}$, independent of the dimension of a more general simulation. Halving the standard error therefore requires roughly four times as many paths.

## 4. Antithetic variance reduction

For every sampled $Z$, the implementation also uses $-Z$. The paired estimator is

$$
\widehat V_{\text{anti}}
=\frac1M\sum_{j=1}^M\frac{f(Z_j)+f(-Z_j)}2,
$$

where $f$ denotes the discounted payoff mapping. Its variance is

$$
\operatorname{Var}\!\left(\frac{f(Z)+f(-Z)}2\right)
=\frac14\left[\operatorname{Var}(f(Z))+\operatorname{Var}(f(-Z))
+2\operatorname{Cov}(f(Z),f(-Z))\right].
$$

For a monotone payoff such as a European call, the two terms tend to be negatively correlated, reducing estimator variance without changing the target expectation.

## 5. Black-Scholes benchmark

The analytical call price is

$$
C_0=S_0\Phi(d_1)-Ke^{-rT}\Phi(d_2),
$$

and the put price is

$$
P_0=Ke^{-rT}\Phi(-d_2)-S_0\Phi(-d_1),
$$

with

$$
d_1=\frac{\log(S_0/K)+(r+\tfrac12\sigma^2)T}{\sigma\sqrt T},
\qquad
d_2=d_1-\sigma\sqrt T.
$$

Agreement between simulation and this closed-form benchmark checks the drift, discounting, payoff and random sampling together.

## 6. Put-call parity

For European options with the same $S_0$, $K$ and $T$,

$$
C_0-P_0=S_0-Ke^{-rT}.
$$

The test suite verifies this identity numerically for the analytical implementation.

## 7. Assumptions and limitations

The model assumes constant volatility and interest rates, continuous trading, lognormal prices, no dividends, frictionless markets and European exercise. Real markets exhibit volatility smiles, jumps, stochastic volatility, bid-ask spreads and discrete hedging. Extensions could include dividend yield, path-dependent payoffs, control variates, quasi-Monte Carlo or calibration to an implied-volatility surface.

## 8. Validation

The tests check that a 200,000-path confidence interval contains the Black-Scholes benchmark, put-call parity holds and identical seeds reproduce identical estimates.
