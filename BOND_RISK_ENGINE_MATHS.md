# Bond Yield-Curve and Risk Engine - Mathematical Notes

[Back to the portfolio](README.md) · [View the implementation](bond_risk_engine.py) · [View the tests](test_bond_risk_engine.py)

## 1. Cash flows and zero-curve pricing

For face value $F$, annual coupon rate $c$, payment frequency $m$ and maturity $T$, each regular coupon is

$$
C=\frac{Fc}{m}.
$$

At the final payment date, the investor receives $C+F$. If $z(t_i)$ is the continuously compounded zero rate at payment time $t_i$, the discount factor is

$$
D(t_i)=e^{-z(t_i)t_i},
$$

and the no-arbitrage bond price is

$$
P=\sum_{i=1}^{mT}CF_iD(t_i).
$$

The implementation linearly interpolates zero rates between curve nodes before applying exponential discounting.

## 2. Bootstrapping from par yields

The bootstrap routine uses annual par bonds with unit face value. For the $n$-year instrument with par coupon $c_n$, price equals par:

$$
1=c_n\sum_{i=1}^{n-1}D_i+(1+c_n)D_n.
$$

Once $D_1,\ldots,D_{n-1}$ are known, the next discount factor is

$$
D_n=\frac{1-c_n\sum_{i=1}^{n-1}D_i}{1+c_n}.
$$

The continuously compounded zero rate follows from $D_n=e^{-z_nn}$:

$$
z_n=-\frac{\log D_n}{n}.
$$

This sequential structure is why the procedure is called bootstrapping: each new maturity uses discount factors already recovered from shorter maturities.

## 3. Yield to maturity

Yield to maturity compresses the entire curve into a single periodically compounded rate $y$ satisfying

$$
P_{\text{market}}=\sum_{i=1}^{mT}\frac{CF_i}{(1+y/m)^{mt_i}}.
$$

There is generally no convenient closed-form inverse for a coupon bond, so the code solves

$$
f(y)=P(y)-P_{\text{market}}=0
$$

by bisection. For standard positive cash flows, $P(y)$ is decreasing in $y$, making the root unique over a valid bracket.

## 4. Duration

Macaulay duration is the present-value-weighted average payment time:

$$
D_{\text{Mac}}=\frac{\sum_i t_iPV(CF_i)}{P}.
$$

Modified duration converts this timing measure into first-order price sensitivity:

$$
D_{\text{mod}}=\frac{D_{\text{Mac}}}{1+y/m},
\qquad
\frac{\Delta P}{P}\approx-D_{\text{mod}}\Delta y.
$$

The negative sign captures the inverse relationship between yield and price.

## 5. Convexity

Duration is only a tangent approximation. For coupon-period index $n_i=mt_i$, the implementation uses

$$
\mathcal C=\frac1{Pm^2}\sum_i
\frac{CF_i\,n_i(n_i+1)}{(1+y/m)^{n_i+2}}.
$$

Adding the second-order term gives

$$
\frac{\Delta P}{P}\approx-D_{\text{mod}}\Delta y
+\frac12\mathcal C(\Delta y)^2.
$$

For an ordinary option-free bond, positive convexity means the price gain from a yield fall is larger than the price loss from an equal yield rise, all else equal.

## 6. Curve-shock scenarios

If a curve node has zero rate $z_j$, a shock of $b_j$ basis points creates

$$
z_j^{\text{shock}}=z_j+\frac{b_j}{10{,}000}.
$$

The engine reprices the bond under four deterministic scenarios:

- parallel $-100$ bp;
- parallel $+100$ bp;
- a steepener ranging linearly from $-50$ bp at the short end to $+50$ bp at the long end; and
- the opposite flattener.

For each scenario,

$$
\text{P\&L}=P_{\text{shock}}-P_{\text{base}},
\qquad
R=\frac{P_{\text{shock}}}{P_{\text{base}}}-1.
$$

Full repricing captures curve non-linearity that a single duration number cannot.

## 7. Assumptions and limitations

The engine assumes deterministic cash flows and does not model default, recovery, embedded options, accrued interest, day-count conventions, liquidity or stochastic rates. Linear interpolation of zero rates is intentionally simple. Production fixed-income systems would use instrument-specific calendars and conventions, calibrated curve interpolation and separate credit and liquidity components.

## 8. Validation

The tests verify that a par coupon bond prices at par on a matching flat curve, YTM recovers the coupon rate for a par bond, duration is positive and below maturity, and parallel rate shocks move price in the expected direction.
