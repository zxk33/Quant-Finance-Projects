# Mathematics: Comparing Inventory Policies

This research compares *simulated* quoting policies on matched random scenarios. It uses separate train, validation and held-out test simulations.

## 1. Matched-policy comparison

For simulation path \(j\), let \(X_j^{(A)}\) and \(X_j^{(B)}\) be a metric (e.g., P&L, maximum inventory or loss indicator) under two policies.

$$
D_j=X_j^{(A)}-X_j^{(B)}, \qquad
\overline D=\frac{1}{N}\sum_{j=1}^{N}D_j.
$$

Using the same random path for both policies helps isolate the policy effect and can reduce the variance of the difference.

## 2. Dispersion and risk metrics

For simulated P&L values \(P_1,\ldots,P_N\):

$$
\overline P=\frac{1}{N}\sum_{j=1}^{N}P_j,
\qquad
s_P=\sqrt{\frac{1}{N-1}\sum_{j=1}^{N}(P_j-\overline P)^2}.
$$

Other reported diagnostics include the fraction of loss-making paths, maximum inventory and adverse tail outcomes.

## 3. Separation of development and testing

Tune candidate policies using training simulations, compare them using validation simulations, and evaluate the final selected policy on *independent held-out* simulations. Do not choose parameters using the final test set.

## Limitations

All results are specific to the simulation's price, flow, fill and cost assumptions. Stress cases can test robustness to changed assumptions but do not establish expected live-market performance.
