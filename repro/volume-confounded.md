# Repro: volume-confounded concentration (case volume-confounded-hhi)

`paired_delta.parquet` holds the twenty per-seed paired differences
(L4 attacker minus uniform null) behind the case:

- `delta_percentile_midrank`: within-offer wealth percentile of the
  chosen target, computed against engine cash. Positive on 20/20 seeds
  (the attacker aims).
- `delta_hhi`: recipient HHI difference. Negative on 18/20 seeds: the
  attacker bribes about four times more often, and concentration
  shrinks mechanically with volume.

Reading the raw HHI comparison alone would conclude the attacker is
less concentrating than chance; the percentile column and the
conditional permutation test (see the world-100-grid dataset verify.py,
claims D and F) show the opposite. Countermeasure: condition on the
recorded offer sets and match volume before comparing concentration.

Source: alashi docs/ops/WORLD_100_BLIND_ABLATION_20261113.md.
