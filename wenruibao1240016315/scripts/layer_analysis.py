"""Layer-composition analysis: how much of the cross-system difference is
explained by the different OS-layer mix of the three samples?

The paper compares the three systems on the whole set of 500 defects each.  The
three samples differ strongly in *where* the defects live (HarmonyOS is 72 %
kernel, Linux 54 % application layer, Android 39 % system service).  This script
asks whether the differences reported for affected functions and trigger
scenarios are partly a consequence of that composition, by:

  1. tabulating the layer composition of each system (`layer_composition.csv`);
  2. comparing the systems inside each shared layer (`layer_within_*.csv`,
     `layer_pairwise_*.csv`);
  3. standardising each system to a common layer mix — pooled over the three
     systems, and uniform over the shared layers (`layer_distances.csv`);
  4. comparing the raw, within-layer and standardised distances, and drawing the
     two summary figures (`figures/`).

Layers with fewer than MIN_N defects in any system are excluded from the
within-layer and standardised comparisons and reported separately, because a
distribution estimated from a handful of defects is not interpretable.

Usage:
    python scripts/layer_analysis.py [--data DIR] [--results DIR] [--figures DIR]
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter

import common as C

MIN_N = 10
DIMENSIONS = (
    ("function", "Affected Function", C.FUNCTION,
     C.CATEGORY_ORDER["affected_function"]),
    ("trigger", "Trigger Scenario", C.TRIGGER,
     C.CATEGORY_ORDER["trigger_scenario"]),
)
PAIRS = (("android", "linux"), ("android", "harmony"), ("linux", "harmony"))


def counts(rows, field, table, categories):
    counter = Counter(table[row[field]] for row in rows)
    return [counter.get(cat, 0) for cat in categories]


def as_distribution(values):
    total = sum(values)
    if total == 0:
        raise ValueError("cannot normalise an all-zero vector")
    return [v / total for v in values]


def jsd(p, q):
    """Jensen-Shannon distance (base 2): 0 = identical, 1 = disjoint support."""
    p = as_distribution(p)
    q = as_distribution(q)
    m = [(a + b) / 2.0 for a, b in zip(p, q)]

    def kl(x, y):
        return sum(a * math.log2(a / b) for a, b in zip(x, y) if a > 0)

    return math.sqrt(max(0.0, 0.5 * kl(p, m) + 0.5 * kl(q, m)))


def layer_rows(data, system, layer):
    return [row for row in data[system] if C.LAYER[row["OS Layer"]] == layer]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=str(C.DATA_DIR))
    parser.add_argument("--results", default=str(C.RESULTS_DIR))
    parser.add_argument("--figures", default=str(C.ROOT / "figures"))
    args = parser.parse_args(argv)

    data = C.load_dataset(args.data)
    results = C.Path(args.results)
    figures = C.Path(args.figures)
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    total_defects = sum(len(rows) for rows in data.values())

    # ------------------------------------------------------------------
    # 1. Layer composition
    # ------------------------------------------------------------------
    composition = []
    per_layer = {}
    for system in C.SYSTEMS:
        counter = Counter(C.LAYER[row["OS Layer"]] for row in data[system])
        per_layer[system] = counter
        for layer in C.CATEGORY_ORDER["os_layer"]:
            n = counter.get(layer, 0)
            composition.append({
                "system": system,
                "layer": layer,
                "defects": n,
                "share_pct": round(100.0 * n / len(data[system]), 2),
                "pooled_share_pct": "",
            })

    # pooled shares and common-support flag are added once all systems are known
    pooled = {layer: sum(per_layer[s].get(layer, 0) for s in C.SYSTEMS)
              for layer in C.CATEGORY_ORDER["os_layer"]}
    common = [layer for layer in C.CATEGORY_ORDER["os_layer"]
              if all(per_layer[s].get(layer, 0) >= MIN_N for s in C.SYSTEMS)]
    for row in composition:
        row["pooled_share_pct"] = round(100.0 * pooled[row["layer"]] / total_defects, 2)
        row["common_support"] = "yes" if row["layer"] in common else "no"
        row["excluded_reason"] = ("" if row["layer"] in common else
                                  f"fewer than {MIN_N} defects in at least one system")
    C.write_rows(results / "layer_composition.csv",
                 ["system", "layer", "defects", "share_pct", "pooled_share_pct",
                  "common_support", "excluded_reason"], composition)

    # ------------------------------------------------------------------
    # 2. Within-layer distributions
    # ------------------------------------------------------------------
    within_rows = []
    for dim_key, field, table, categories in DIMENSIONS:
        rows = []
        for system in C.SYSTEMS:
            for layer in C.CATEGORY_ORDER["os_layer"]:
                subset = layer_rows(data, system, layer)
                if not subset:
                    continue
                counts_vec = counts(subset, field, table, categories)
                for cat, n in zip(categories, counts_vec):
                    rows.append({"system": system, "layer": layer,
                                 "n_layer": len(subset), "category": cat,
                                 "defects": n,
                                 "share_in_layer_pct": round(100.0 * n / len(subset), 2)})
        C.write_rows(results / f"layer_within_{dim_key}.csv",
                     ["system", "layer", "n_layer", "category", "defects",
                      "share_in_layer_pct"], rows)
        within_rows.append((dim_key, rows))

    # ------------------------------------------------------------------
    # 3. Pairwise distances inside each shared layer
    # ------------------------------------------------------------------
    for dim_key, field, table, categories in DIMENSIONS:
        rows = []
        for layer in common:
            for left, right in PAIRS:
                left_rows = layer_rows(data, left, layer)
                right_rows = layer_rows(data, right, layer)
                rows.append({
                    "layer": layer,
                    "pair": f"{left}-{right}",
                    "n_a": len(left_rows), "n_b": len(right_rows),
                    "jsd": round(jsd(counts(left_rows, field, table, categories),
                                     counts(right_rows, field, table, categories)), 4),
                })
        C.write_rows(results / f"layer_pairwise_{dim_key}.csv",
                     ["layer", "pair", "n_a", "n_b", "jsd"], rows)

    # ------------------------------------------------------------------
    # 4. Standardisation and the before/after comparison
    # ------------------------------------------------------------------
    common_total = sum(pooled[layer] for layer in common)
    weights_pooled = {layer: pooled[layer] / common_total for layer in common}
    weights_uniform = {layer: 1.0 / len(common) for layer in common}

    def standardise(system, field, table, categories, weights):
        vector = [0.0] * len(categories)
        for layer, weight in weights.items():
            subset = layer_rows(data, system, layer)
            if not subset:
                continue
            dist = as_distribution(counts(subset, field, table, categories))
            for i, value in enumerate(dist):
                vector[i] += weight * value
        return vector

    distances = []
    raw_vectors = {}
    for dim_key, field, table, categories in DIMENSIONS:
        raw = {s: counts(data[s], field, table, categories) for s in C.SYSTEMS}
        std_pooled = {s: standardise(s, field, table, categories, weights_pooled)
                      for s in C.SYSTEMS}
        std_uniform = {s: standardise(s, field, table, categories, weights_uniform)
                       for s in C.SYSTEMS}
        raw_vectors[dim_key] = raw

        for left, right in PAIRS:
            d_raw = jsd(raw[left], raw[right])
            d_pooled = jsd(std_pooled[left], std_pooled[right])
            d_uniform = jsd(std_uniform[left], std_uniform[right])
            within = sum(weights_pooled[layer] *
                         jsd(counts(layer_rows(data, left, layer), field, table, categories),
                             counts(layer_rows(data, right, layer), field, table, categories))
                         for layer in common)
            distances.append({
                "dimension": dim_key,
                "pair": f"{left}-{right}",
                "jsd_raw": round(d_raw, 4),
                "jsd_standardised_pooled": round(d_pooled, 4),
                "jsd_standardised_uniform": round(d_uniform, 4),
                "jsd_within_layer": round(within, 4),
                "explained_by_composition_pct": round(100.0 * (d_raw - d_pooled) / d_raw, 1),
                "explained_uniform_pct": round(100.0 * (d_raw - d_uniform) / d_raw, 1),
            })
    C.write_rows(results / "layer_distances.csv",
                 ["dimension", "pair", "jsd_raw", "jsd_standardised_pooled",
                  "jsd_standardised_uniform", "jsd_within_layer",
                  "explained_by_composition_pct", "explained_uniform_pct"], distances)

    # ------------------------------------------------------------------
    # 5. Figures
    # ------------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = "cs340-layer"
    import matplotlib.pyplot as plt

    layers = [layer for layer in C.CATEGORY_ORDER["os_layer"]]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    bottom = {system: 0.0 for system in C.SYSTEMS}
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860"]
    for i, layer in enumerate(layers):
        shares = [100.0 * per_layer[s].get(layer, 0) / len(data[s]) for s in C.SYSTEMS]
        ax.barh(list(C.SYSTEMS), shares, left=[bottom[s] for s in C.SYSTEMS],
                color=colors[i], label=layer, height=0.55)
        for j, system in enumerate(C.SYSTEMS):
            bottom[system] += shares[j]
    ax.set_xlabel("Share of the 500 defects per system (%)")
    ax.set_title("OS-layer composition of the three samples")
    ax.legend(fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.22),
              frameon=False)
    ax.set_xlim(0, 100)
    fig.tight_layout()
    fig.savefig(figures / "layer_composition.png", dpi=200)
    fig.savefig(figures / "layer_composition.svg", metadata={"Date": None})
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6), sharey=True)
    labels = [f"{a[:3]}-{b[:3]}" for a, b in PAIRS]
    for ax, (dim_key, _field, _table, _cats) in zip(axes, DIMENSIONS):
        subset = [d for d in distances if d["dimension"] == dim_key]
        raw_v = [d["jsd_raw"] for d in subset]
        pooled_v = [d["jsd_standardised_pooled"] for d in subset]
        uniform_v = [d["jsd_standardised_uniform"] for d in subset]
        x = range(len(labels))
        ax.bar([i - 0.26 for i in x], raw_v, width=0.26, label="raw",
               color="#999999")
        ax.bar(list(x), pooled_v, width=0.26, label="standardised (pooled)",
               color="#4C72B0")
        ax.bar([i + 0.26 for i in x], uniform_v, width=0.26,
               label="standardised (uniform)", color="#DD8452")
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 0.8)
        ax.set_title("Affected function" if dim_key == "function" else "Trigger scenario")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Jensen-Shannon distance")
    axes[0].legend(fontsize=7, frameon=False, loc="upper right")
    fig.suptitle("Cross-system distance before and after controlling for layer mix",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(figures / "layer_distance_adjustment.png", dpi=200)
    fig.savefig(figures / "layer_distance_adjustment.svg", metadata={"Date": None})
    plt.close(fig)

    # ------------------------------------------------------------------
    # 6. Console summary
    # ------------------------------------------------------------------
    print(f"layers with >= {MIN_N} defects in all three systems: {', '.join(common)}")
    print("excluded: " + ", ".join(layer for layer in layers if layer not in common))
    print(f"pooled weights: " + ", ".join(
        f"{layer}={weights_pooled[layer]:.3f}" for layer in common))
    print()
    for dim_key, _f, _t, _c in DIMENSIONS:
        print(dim_key)
        for d in distances:
            if d["dimension"] != dim_key:
                continue
            print(f"  {d['pair']:17s} raw={d['jsd_raw']:.3f}  "
                  f"pooled={d['jsd_standardised_pooled']:.3f}  "
                  f"uniform={d['jsd_standardised_uniform']:.3f}  "
                  f"within={d['jsd_within_layer']:.3f}  "
                  f"explained={d['explained_by_composition_pct']:+.1f}%")
    print(f"\nwrote {results} and {figures}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
