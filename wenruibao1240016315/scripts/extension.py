"""Extension: is the cross-system (dis)similarity conclusion metric-dependent?

The paper compares the three systems with Spearman's rank correlation over
category vectors (Figure 4).  Rank correlation ignores magnitudes: two systems
that put 40% and 80% of their defects in the same category look identical to it.
This experiment keeps the data and the category sets fixed and changes one
factor -- the similarity measure -- to a magnitude-sensitive one, the
Jensen-Shannon distance between the percentage distributions.

Question: do the paper's conclusions ("the systems are broadly dissimilar")
survive the change of metric, and does the ranking of the three pairs agree?

Usage:
    python scripts/extension.py [--out results/extension_jsd.csv]
"""

from __future__ import annotations

import argparse
import math
import sys

import common as C

PANELS = ("a_os_layer", "b_affected_function", "c_trigger_scenario", "d_overall")


def js_distance(p, q):
    """Jensen-Shannon distance (square root of the divergence), base 2."""
    sp, sq = sum(p), sum(q)
    if sp <= 0 or sq <= 0:
        raise ValueError("empty distribution")
    p = [v / sp for v in p]
    q = [v / sq for v in q]
    m = [(a + b) / 2.0 for a, b in zip(p, q)]

    def kl(x, y):
        total = 0.0
        for a, b in zip(x, y):
            if a > 0:
                total += a * math.log2(a / b)
        return total

    return math.sqrt(max(0.0, 0.5 * kl(p, m) + 0.5 * kl(q, m)))


def panel_vectors(data):
    counts = {p: C.panel_counts(data, p) for p in C.TABLE2_PANELS}
    out = {}
    for panel in ("a_os_layer", "b_affected_function", "c_trigger_scenario"):
        key = panel[2:]
        out[panel] = {s: C.panel_vector(counts, key, s) for s in C.SYSTEMS}
    joined = {}
    for system in C.SYSTEMS:
        vec = []
        for key in ("os_layer", "affected_function", "trigger_scenario"):
            vec.extend(C.panel_vector(counts, key, system))
        joined[system] = vec
    out["d_overall"] = joined
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=str(C.DATA_DIR))
    parser.add_argument("--out", default=str(C.RESULTS_DIR / "extension_jsd.csv"))
    args = parser.parse_args(argv)

    data = C.load_dataset(args.data)
    vecs = panel_vectors(data)

    rows = []
    for panel in PANELS:
        values = []
        for left, right in C.PAIRS:
            x, y = vecs[panel][left], vecs[panel][right]
            rho = C.spearman(*C.drop_double_zero(x, y))
            dist = js_distance(x, y)
            values.append((f"{left}-{right}", rho, dist))
        # rank 1 = most similar: highest rho / lowest distance
        by_rho = {pair: i + 1 for i, (pair, _, _)
                  in enumerate(sorted(values, key=lambda t: -t[1]))}
        by_jsd = {pair: i + 1 for i, (pair, _, _)
                  in enumerate(sorted(values, key=lambda t: t[2]))}
        for pair, rho, dist in values:
            rows.append({"panel": panel, "pair": pair,
                         "spearman": f"{rho:.2f}",
                         "jsd": f"{dist:.4f}",
                         "rank_spearman": by_rho[pair],
                         "rank_jsd": by_jsd[pair],
                         "same_rank": "yes" if by_rho[pair] == by_jsd[pair] else "NO"})

    C.write_rows(args.out, ["panel", "pair", "spearman", "jsd",
                            "rank_spearman", "rank_jsd", "same_rank"], rows)

    for panel in PANELS:
        subset = [r for r in rows if r["panel"] == panel]
        same = sum(r["same_rank"] == "yes" for r in subset)
        print(f"{panel:22s} ranks agree: {same}/3")
        for r in subset:
            print(f"   {r['pair']:17s} rho={r['spearman']:>6s}  "
                  f"JSD={r['jsd']}  rank {r['rank_spearman']} vs {r['rank_jsd']}")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
