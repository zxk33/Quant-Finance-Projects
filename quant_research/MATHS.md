# Mathematics: Inventory-Policy Research

The inventory study compares candidate quoting policies under independent
training, validation and held-out simulation sets.

For a metric X measured on paired simulations, the policy effect is estimated
from matched differences

[
D_j = X_j^{policy} - X_j^{control},
qquad
ar D = rac{1}{N}sum_{j=1}^{N}D_j.
]

Using the same random path for both policies reduces variance in the comparison.

For P&L samples P_1,...,P_N, the sample volatility is

[
s_P = sqrt{rac{1}{N-1}sum_j(P_j-ar P)^2}.
]

The research also records loss frequency, maximum inventory and tail outcomes,
then re-runs policies under changed volatility, informed-flow and transaction
cost assumptions. Candidate policies are selected before the final held-out
test so that the test set is not used for tuning.
