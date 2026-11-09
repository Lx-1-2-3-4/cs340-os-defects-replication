#!/usr/bin/env python3
"""Record-bootstrap uncertainty for Figure 4(a-c) cross-OS correlations.

The original reproduction checks the nine reported Spearman coefficients as
point estimates. This extension resamples defect records independently within
each OS, rebuilds the three Figure 4 category distributions in every draw,
and recomputes the three OS-pair correlations. The same sampled records are
used for all three dimensions in a draw, preserving their within-record
dependence.

Only the dimensions shown in Figure 4(a-c) are included. Panel (d) is excluded
because the source replication documents that its construction is unspecified
and its reported values do not match the released records.

Usage (from the member repository directory):
    python extension/figure4_bootstrap.py
    python extension/figure4_bootstrap.py --bootstrap-resamples 20000 --seed 7
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import common  # noqa: E402

PANELS = (
    ("a_os_layer", "os_layer", "OS layer"),
    ("b_affected_function", "affected_function", "Affected function"),
    ("c_trigger_scenario", "trigger_scenario", "Trigger scenario"),
)
FIELDS = (
    ("OS Layer", common.OS_LAYER_LABEL),
    ("Affected Function", common.AFFECTED_FUNCTION_LABEL),
    ("Trigger Scenario", common.TRIGGER_LABEL),
)


def quantile(sorted_values: list[float], probability: float) -> float:
    """Linearly interpolate the empirical quantile."""
    if not sorted_values:
        raise ValueError("cannot compute a quantile from no values")
    position = (len(sorted_values) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def paper_panel_vectors(records: dict) -> dict:
    """Return observed count vectors in the category order used by Figure 4."""
    vectors = {}
    for _, panel, _ in PANELS:
        counts = common.panel_counts(records, panel)
        vectors[panel] = {
            tag: [counts[tag].get(category, 0) for category in common.PANEL_COLUMNS[panel]]
            for tag in common.OS_TAGS
        }
    return vectors


def coefficient(left: str, right: str, vectors: dict) -> float:
    x, y = common.drop_shared_zeros(vectors[left], vectors[right])
    return common.spearman(x, y)


def encoded_records(records: dict) -> dict:
    """Encode each record as (layer, function, trigger) category indexes."""
    encoded = {}
    for tag, rows in records.items():
        os_rows = []
        for row in rows:
            indexes = []
            for (field, mapping), (_, panel, _) in zip(FIELDS, PANELS):
                label = mapping[row[field]]
                indexes.append(common.PANEL_COLUMNS[panel].index(label))
            os_rows.append(tuple(indexes))
        encoded[tag] = os_rows
    return encoded


def bootstrap_coefficients(encoded: dict, rng: random.Random) -> dict:
    """Draw one stratified bootstrap replicate and compute all nine rhos."""
    counts = {
        panel: {
            tag: [0] * len(common.PANEL_COLUMNS[panel])
            for tag in common.OS_TAGS
        }
        for _, panel, _ in PANELS
    }

    # Resampling individual defect rows preserves associations among the three
    # dimensions while keeping each OS at its original sample size of 500.
    for tag in common.OS_TAGS:
        rows = encoded[tag]
        # random() has a documented stable sequence for a fixed seed, which
        # keeps these sampled indices reproducible across Python 3 versions.
        sampled = (int(rng.random() * len(rows)) for _ in range(len(rows)))
        for row_index in sampled:
            layer_index, function_index, trigger_index = rows[row_index]
            counts["os_layer"][tag][layer_index] += 1
            counts["affected_function"][tag][function_index] += 1
            counts["trigger_scenario"][tag][trigger_index] += 1

    result = {}
    for paper_panel, panel, _ in PANELS:
        for left, right in common.PAIRS:
            key = (paper_panel, left, right)
            try:
                result[key] = coefficient(left, right, counts[panel])
            except ValueError:
                # A constant category-count vector makes Spearman undefined.
                result[key] = None
    return result


def make_report(
    rows: list[dict], resamples: int, seed: int, data_hashes: dict, python_version: str
) -> str:
    lines = [
        "# Figure 4(a-c): uncertainty in cross-OS defect-profile correlations",
        "",
        "## Argument and replication",
        "",
        "The paper's Figure 4 and Finding 5 argue that defect-category profiles",
        "differ across Android, Linux, and HarmonyOS. The existing reproduction",
        "already matches all nine printed Spearman coefficients in panels (a)-(c).",
        "This experiment adds record-level uncertainty intervals for those same",
        "coefficients; it does not re-run the paper's Figure 4(d) analysis.",
        "",
        "The experiment independently resamples 500 defect records with replacement",
        "within each OS. For every replicate, it rebuilds the OS-layer, affected-",
        "function, and trigger-scenario counts from the same sampled records, then",
        "computes Spearman's rho for each OS pair. Categories that are zero in both",
        "OS samples are dropped, following the existing Figure 4 reproduction rule.",
        "The reported intervals are the 2.5th and 97.5th empirical percentiles.",
        "The two stability columns show how often a replicate keeps the observed",
        "sign and how often its absolute correlation is below the paper's 0.4",
        "weak-correlation boundary.",
        "",
        "## Results",
        "",
        "| Figure panel | OS pair | Categories | Paper rho | Recomputed rho | 95% bootstrap interval | Same sign | \\|rho\\| < 0.4 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['panel_label']} | {row['pair']} | {row['category_count']} | "
            f"{float(row['paper_rho']):.2f} | {float(row['observed_rho']):.2f} | "
            f"[{float(row['ci95_low']):.2f}, {float(row['ci95_high']):.2f}] | "
            f"{float(row['same_sign_pct']):.1f}% | {float(row['abs_rho_below_0_4_pct']):.1f}% |"
        )
    matches = sum(row["point_match"] == "yes" for row in rows)
    lines += [
        "",
        "## Interpretation and limits",
        "",
        f"The original point estimates reproduce {matches}/{len(rows)} exactly to the",
        "paper's two-decimal precision. The intervals describe sensitivity of the",
        "released 500-record samples to record resampling. They are not population-",
        "level confidence intervals: the paper selected the latest 500 records per",
        "OS rather than drawing a probability sample, and each rho is calculated",
        "across only 6-8 fixed taxonomy categories. These results can show whether",
        "the reported category ranking is stable under this resampling scheme, but",
        "cannot establish that the same correlations hold for all OS defects.",
        "",
        f"Settings: {resamples:,} bootstrap replicates; seed {seed}; 500 records per OS;",
        f"Python {python_version}; percentile interval; category order and shared-zero",
        "rule inherited from scripts/common.py. Sampling uses the stable random.Random.random() stream.",
        "",
        "Input SHA-256 (from the committed dataset snapshot):",
    ]
    for filename, digest in sorted(data_hashes.items()):
        lines.append(f"- {filename}: {digest}")
    lines += [
        "",
        "Run from the member folder with python extension/figure4_bootstrap.py.",
        "The script writes this report and figure4_bootstrap.csv under",
        "extension/results/.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(common.DEFAULT_DATA_DIR))
    parser.add_argument("--paper-dir", default=str(common.DEFAULT_PAPER_DIR))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "extension" / "results"))
    parser.add_argument("--bootstrap-resamples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20261109)
    args = parser.parse_args(argv)
    if args.bootstrap_resamples < 100:
        parser.error("--bootstrap-resamples must be at least 100")

    records = common.load_defects(args.data_dir)
    observed_vectors = paper_panel_vectors(records)
    paper_rows = common.load_paper_values(args.paper_dir)["fig4"]
    panels = {item[0] for item in PANELS}
    paper_lookup = {
        (row["panel"], row["pair"]): float(row["paper_rho"])
        for row in paper_rows
        if row["panel"] in panels
    }

    observed = {}
    for paper_panel, panel, _ in PANELS:
        for left, right in common.PAIRS:
            key = (paper_panel, left, right)
            observed[key] = coefficient(left, right, observed_vectors[panel])
            paper_key = (paper_panel, f"{left}-{right}")
            if paper_key not in paper_lookup:
                raise ValueError(f"paper reference is missing Figure 4 value {paper_key}")
            if common.fmt_rho(observed[key]) != common.fmt_rho(paper_lookup[paper_key]):
                raise ValueError(
                    f"point estimate mismatch for {paper_key}: observed "
                    f"{observed[key]:.2f}, paper {paper_lookup[paper_key]:.2f}"
                )

    encoded = encoded_records(records)
    rng = random.Random(args.seed)
    samples = defaultdict(list)
    undefined = defaultdict(int)
    for _ in range(args.bootstrap_resamples):
        replicate = bootstrap_coefficients(encoded, rng)
        for key, value in replicate.items():
            if value is None:
                undefined[key] += 1
            else:
                samples[key].append(value)

    rows = []
    for paper_panel, panel, panel_label in PANELS:
        for left, right in common.PAIRS:
            key = (paper_panel, left, right)
            draws = sorted(samples[key])
            if not draws:
                raise RuntimeError(f"all bootstrap replicates were undefined for {key}")
            point = observed[key]
            same_sign = sum(point * draw > 0 for draw in draws) / len(draws)
            weak = sum(abs(draw) < 0.4 for draw in draws) / len(draws)
            pair_label = f"{common.OS_DISPLAY[left]}–{common.OS_DISPLAY[right]}"
            category_count = len(common.drop_shared_zeros(
                observed_vectors[panel][left], observed_vectors[panel][right]
            )[0])
            rows.append({
                "panel": paper_panel,
                "panel_label": panel_label,
                "pair": pair_label,
                "category_count": category_count,
                "paper_rho": f"{paper_lookup[(paper_panel, f'{left}-{right}')]:.2f}",
                "observed_rho": f"{point:.6f}",
                "point_match": "yes",
                "ci95_low": f"{quantile(draws, 0.025):.6f}",
                "ci95_high": f"{quantile(draws, 0.975):.6f}",
                "same_sign_pct": f"{100.0 * same_sign:.2f}",
                "abs_rho_below_0_4_pct": f"{100.0 * weak:.2f}",
                "valid_resamples": len(draws),
                "undefined_resamples": undefined[key],
            })

    out_dir = Path(args.out_dir)
    csv_fields = [
        "panel", "panel_label", "pair", "category_count", "paper_rho",
        "observed_rho", "point_match", "ci95_low", "ci95_high",
        "same_sign_pct", "abs_rho_below_0_4_pct", "valid_resamples",
        "undefined_resamples",
    ]
    common.write_csv(out_dir / "figure4_bootstrap.csv", csv_fields, rows)
    data_hashes = common.data_sha256(args.data_dir)
    common.write_text(
        out_dir / "figure4_bootstrap.md",
        make_report(
            rows,
            args.bootstrap_resamples,
            args.seed,
            data_hashes,
            common.environment_info()["python_version"],
        ),
    )
    print("verified 9/9 Figure 4(a-c) point estimates against the paper")
    print(f"completed {args.bootstrap_resamples:,} stratified bootstrap replicates")
    print(f"wrote {out_dir / 'figure4_bootstrap.csv'}")
    print(f"wrote {out_dir / 'figure4_bootstrap.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
