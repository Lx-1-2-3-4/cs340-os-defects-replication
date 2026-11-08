"""Investigate Figure 4 panel (d), the only set of values that does not reproduce.

The paper's heatmap (d) prints Android-Linux = 0.05, Android-HarmonyOS = -0.11 and
HarmonyOS-Linux = -0.04, but never says how the "overall" vector is built.  This
script evaluates a family of plausible rules and writes every result, so the
report can show that the panel is under-specified rather than mis-computed.

Usage:
    python scripts/fig4d_candidates.py [--out results/fig4d_candidates.csv]
"""

from __future__ import annotations

import argparse
import math
import sys
from itertools import combinations

import common as C

PAPER = {("android", "linux"): 0.05,
         ("android", "harmony"): -0.11,
         ("linux", "harmony"): -0.04}
PANELS_ABC = ("os_layer", "affected_function", "trigger_scenario")
PANELS_ALL = C.TABLE2_PANELS


def vectors(data, panels):
    counts = {p: C.panel_counts(data, p) for p in panels}
    out = {}
    for system in C.SYSTEMS:
        vec = []
        for p in panels:
            vec.extend(C.panel_vector(counts, p, system))
        out[system] = vec
    return out


def rho_drop(vecs):
    result = {}
    for left, right in C.PAIRS:
        x, y = C.drop_double_zero(vecs[left], vecs[right])
        result[(left, right)] = C.spearman(x, y)
    return result


def rho_keep(vecs):
    return {(l, r): C.spearman(vecs[l], vecs[r]) for l, r in C.PAIRS}


def mean_of_panels(data, panels):
    """Average the per-panel coefficients instead of pooling the vectors."""
    per_panel = {}
    for p in panels:
        vecs = vectors(data, (p,))
        per_panel[p] = rho_keep(vecs)
    return {pair: sum(per_panel[p][pair] for p in panels) / len(panels)
            for pair in C.PAIRS}


def fisher_mean(data, panels):
    """Back-transform the mean of the Fisher z of the per-panel coefficients."""
    per_panel = {}
    for p in panels:
        vecs = vectors(data, (p,))
        per_panel[p] = rho_keep(vecs)
    out = {}
    for pair in C.PAIRS:
        zs = [math.atanh(max(min(per_panel[p][pair], 0.999999), -0.999999))
              for p in panels]
        out[pair] = math.tanh(sum(zs) / len(zs))
    return out


def per_panel_drop_then_pool(data):
    """Drop double-zero categories inside each panel, then pool the survivors."""
    counts = {p: C.panel_counts(data, p) for p in PANELS_ABC}
    joined = {}
    for system in C.SYSTEMS:
        vec = []
        for p in PANELS_ABC:
            vec.extend(C.panel_vector(counts, p, system))
        joined[system] = vec
    # The per-panel rule is applied only to panel (c) in the baseline; here we
    # drop categories that are zero for both systems *in every panel they
    # appear in*, which for panels (a) and (b) is a no-op.
    return rho_drop(joined)


def evaluate(data):
    abc = vectors(data, PANELS_ABC)
    everything = vectors(data, PANELS_ALL)
    rules = [
        ("a-c pooled, drop shared zeros", rho_drop(abc)),
        ("a-c pooled, keep zeros", rho_keep(abc)),
        ("a-e pooled, drop shared zeros", rho_drop(everything)),
        ("a-e pooled, keep zeros", rho_keep(everything)),
        ("mean of panel coefficients (a-c)", mean_of_panels(data, PANELS_ABC)),
        ("Fisher-z mean of panels (a-c)", fisher_mean(data, PANELS_ABC)),
        ("mean of panel coefficients (a-e)", mean_of_panels(data, PANELS_ALL)),
        ("Fisher-z mean of panels (a-e)", fisher_mean(data, PANELS_ALL)),
    ]
    rows = []
    for name, result in rules:
        for pair in C.PAIRS:
            ours = round(result[pair], 2)
            rows.append({"rule": name, "pair": f"{pair[0]}-{pair[1]}",
                         "rho": f"{ours:.2f}",
                         "paper": f"{PAPER[pair]:.2f}",
                         "match": "yes" if abs(ours - PAPER[pair]) < 1e-9 else "NO"})
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=str(C.DATA_DIR))
    parser.add_argument("--out", default=str(C.RESULTS_DIR / "fig4d_candidates.csv"))
    args = parser.parse_args(argv)

    data = C.load_dataset(args.data)
    rows = evaluate(data)
    C.write_rows(args.out, ["rule", "pair", "rho", "paper", "match"], rows)

    matched_rules = {r["rule"] for r in rows if r["match"] == "yes"}
    for rule in dict.fromkeys(r["rule"] for r in rows):
        subset = [r for r in rows if r["rule"] == rule]
        hits = sum(r["match"] == "yes" for r in subset)
        values = ", ".join(f"{r['pair']}={r['rho']}" for r in subset)
        print(f"{hits}/3  {rule:38s} {values}")
    print(f"\nrules reproducing the printed panel: {sorted(matched_rules) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
