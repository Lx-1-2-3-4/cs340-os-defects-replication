"""Rebuild the source comparison from frozen public metadata and review decisions."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "scripts"))
from core import PANELS, spearman

START, END = "2023-05-01", "2025-06-30"
BASELINE = ROOT.parents[2] / "liuxin1240013249/data/defects_linux.json"
FIELDS = ("layer", "function", "trigger")
LABELS = {
    field: dict(zip(codes.split(), panel[1]))
    for field, codes, panel in zip(FIELDS, ("K L V F S A", "M P F D N K S G", "I R B C T E L"), PANELS.values())
}
SOURCES = ("LP", "GH")


def read_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def within_window(timestamp):
    return bool(timestamp and START <= timestamp[:10] <= END)


def audit(snapshot, baseline, decisions, patches, report_links):
    baseline_ids = {r["Bug ID"] for r in baseline}
    commits = defaultdict(set)
    for row in baseline:
        for sha in re.findall(r"/commit/([0-9a-f]{40})\b", row["Patch"]):
            commits[sha].add(row["Bug ID"])
    patch_map = defaultdict(list)
    for p in patches:
        patch_map[p["source"], p["id"]].append(p)
    report_index = defaultdict(set)
    for bug_id, evidence in report_links.items():
        if bug_id not in baseline_ids:
            raise ValueError(f"Unknown published bug ID: {bug_id}")
        for url in evidence["github_report_links"]:
            report_index[url].add(bug_id)

    ledger = []
    seen = set()
    for src, candidates in (("LP", snapshot["downstream"]), ("GH", snapshot["upstream"])):
        for row in candidates:
            key = str(row["Bug ID"] if src == "LP" else row["number"])
            review_key = src, key
            if review_key in seen:
                raise ValueError(f"Duplicate candidate {review_key}")
            seen.add(review_key)
            evidence = [p for p in patch_map[review_key] if p.get("sha256")]
            source_fix = row.get("Patch", row.get("html_url", ""))
            paper = [row.get(name, "") for name, _ in PANELS.values()]
            links = set()
            if src == "LP":
                ident = key
                issue_url = f"https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/{key}"
                reported, fixed = row["date_created"], row["date_fix_released"]
                added, deleted = row["Line Additions"], row["Line Deletions"]
                files = row["Modified Files"]
                sha = next(iter(re.findall(r"/commit/([0-9a-f]{40})\b", source_fix)), "")
                reason = "" if key in baseline_ids and row["status"] == "Fix Released" else "Not a released Ubuntu fix in the published cohort"
                title = row["title"]
                severity = row["importance"]
            else:
                issue = row.get("issue") or {}
                ident, issue_url = issue.get("number", ""), issue.get("html_url", "")
                reported, fixed = issue.get("created_at"), row.get("merged_at")
                added, deleted, files = (row.get(k) for k in ("additions", "deletions", "changed_files"))
                sha = row.get("merge_commit_sha") or ""
                title = issue.get("title", row["title"])
                severity = ""
                reason = "" if issue and issue.get("pull_request") is None else "No unique ordinary issue linked by a closing reference"
                links.update(report_index[issue_url])
                links.update(report_index[source_fix])
                candidate_shas = {sha}
                for p in evidence:
                    links.update(set(p.get("linked_lp_ids", [])) & baseline_ids)
                    candidate_shas.update(p.get("commit_refs", []))
                for candidate_sha in candidate_shas:
                    links.update(commits.get(candidate_sha, ()))
                for p in patches:
                    if p["source"] == "LP" and (
                        str(ident) in p.get("linked_gh_ids", [])
                        or key in p.get("linked_gh_ids", [])
                        or (sha and sha in p.get("commit_refs", []))
                    ):
                        links.add(p["id"])
                if links and not reason:
                    reason = "Potential published duplicate or backport requires adjudication"
            size = added + deleted if added is not None and deleted is not None else None
            label = decisions.get(review_key)
            if not reason:
                if not within_window(reported) or not within_window(fixed):
                    reason = "Report or fix falls outside the common UTC window"
                elif size is None or size > 500:
                    reason = "Unavailable patch size or published/API size exceeds 500 changed lines"
            tags = dict.fromkeys(FIELDS, "")
            included = False
            borderline = False
            if not reason:
                if not label:
                    raise ValueError(f"Missing review decision for {review_key}")
                reason = label["reason"]
                if not reason.strip() or label["decision"] not in {"include", "exclude", "borderline"}:
                    raise ValueError(f"Invalid decision for {review_key}")
                included = label["decision"] == "include"
                borderline = label["decision"] == "borderline"
                if included or borderline:
                    if not evidence or (src == "GH" and issue["state"] != "closed"):
                        raise ValueError(f"Included row lacks verified fix/closed issue: {review_key}")
                    tags = {k: LABELS[k][label[k]] if label[k] else "Unknown" for k in FIELDS}
            strict = (included or borderline) and any(p["direct_git_diff"] and (p["additions"], p["deletions"]) == (added, deleted)
                                      for p in evidence)
            ledger.append(dict(os="Linux", project="systemd", experiment="source_sensitivity",
                               source=src, candidate_id=key, defect_id=ident, title=title,
                               issue_url=issue_url, fix_url=source_fix, fix_commit=sha,
                               report_date_utc=reported or "", fix_date_utc=fixed or "",
                               fix_date_type=("ubuntu_fix_released" if src == "LP" else "github_merged_at"),
                               search_period=row.get("period", ""), lines_added=added, lines_deleted=deleted,
                               lines_changed=size, files_changed=files,
                               size_basis=("published_record" if src == "LP" else "github_pr"),
                               **tags, severity_raw=severity, author_layer=paper[0],
                               author_function=paper[1], author_trigger=paper[2],
                               decision="include" if included else "borderline" if borderline else "exclude", decision_evidence=reason,
                               label_status=("single_review" if included or borderline else "not_applicable"),
                               linked_github_reports="|".join(report_links.get(key, {}).get("github_report_links", [])) if src == "LP" else "",
                               comparable_direct_diff=int(strict),
                               possible_baseline_duplicates="|".join(sorted(links)),
                               inspected_diff_urls="|".join(p["fetched_url"] for p in evidence),
                               inspected_diff_sha256="|".join(p["sha256"] for p in evidence)))
    included = [r for r in ledger if r["decision"] == "include"]
    identities = [(r["source"], r["defect_id"]) for r in included]
    if len(identities) != len(set(identities)):
        raise ValueError("Duplicate defect IDs in the included rows")
    gh_commits = [r["fix_commit"] for r in included if r["source"] == "GH"]
    if not all(gh_commits) or len(gh_commits) != len(set(gh_commits)):
        raise ValueError("Missing or duplicate GitHub merge commits")
    return ledger


def scopes(included, borderline):
    yield "all", "All layers", included
    yield "direct_diff", "All layers", [r for r in included if r["comparable_direct_diff"]]
    yield "include_borderline_test", "All layers", included + borderline
    original = [
        dict(r, **{k: r[f"author_{k}"] for k in FIELDS}) if r["source"] == "LP" else r for r in included
    ]
    yield "author_labels", "All layers", original
    for layer in LABELS["layer"].values():
        yield "same_layer", layer, [r for r in included if r["layer"] == layer]
        yield "same_layer_author_labels", layer, [r for r in original if r["layer"] == layer]


def compare(included, borderline):
    for scope, layer, rows in scopes(included, borderline):
        for field in FIELDS:
            groups = {src: Counter(r[field] for r in rows if r["source"] == src) for src in SOURCES}
            n_lp, n_gh = (sum(groups[src].values()) for src in SOURCES)
            for category in (*LABELS[field].values(), "Unknown"):
                lp, gh = (groups[src][category] for src in SOURCES)
                a = 100 * lp / n_lp if n_lp else None
                b = 100 * gh / n_gh if n_gh else None
                yield dict(scope=scope, layer=layer, dimension=field, category=category,
                           lp_n=n_lp, gh_n=n_gh, lp_count=lp, gh_count=gh, lp_pct=a, gh_pct=b,
                           github_minus_launchpad_pp=b-a if a is not None and b is not None else None)


def rank_comparison(included, borderline):
    for scope, layer, rows in scopes(included, borderline):
        for field in FIELDS:
            grouped = {src: [r[field] for r in rows if r["source"] == src] for src in SOURCES}
            counts = {src: Counter(values) for src, values in grouped.items()}
            n_lp, n_gh = (len(grouped[src]) for src in SOURCES)
            rho = None
            status = "descriptive"
            if scope.startswith("same_layer") and field == "layer":
                status = "not_applicable_layer_held_fixed"
            elif min(n_lp, n_gh) < 3:
                status = "withheld_fewer_than_three_records"
            elif any(counts[src]["Unknown"] for src in SOURCES):
                status = "withheld_unknown_categories"
            else:
                try:
                    # Fixed full paper vocabulary, including shared zero categories.
                    x, y = ([counts[src][k] for k in LABELS[field].values()] for src in SOURCES)
                    rho = spearman(x, y)
                except ValueError:
                    status = "undefined_constant_vector"
            yield dict(scope=scope, layer=layer, dimension=field, lp_n=n_lp, gh_n=n_gh, rho=rho, status=status)


def chart(path, rows, title):
    width, step = 1000, 55
    height = 125 + len(rows) * step
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<g font-family="Arial,sans-serif" font-size="15" fill="#17283b">',
           f'<text x="22" y="31" font-size="23" font-weight="bold">{html.escape(title)}</text>',
           f'<text x="22" y="58">Launchpad n={rows[0]["lp_n"]} (blue) | GitHub n={rows[0]["gh_n"]} (orange)</text>']
    for i, row in enumerate(rows):
        y = 92 + i * step
        out.append(f'<text x="22" y="{y+15}">{html.escape(row["category"])}</text>')
        for n, (prefix, color) in enumerate((("lp", "#2463a6"), ("gh", "#ac501a"))):
            value = row[f"{prefix}_pct"]
            if value is None:
                raise ValueError("Chart requires nonempty cohorts")
            bar = 4.9 * value
            by = y + 19 * n
            out.append(f'<rect x="365" y="{by}" width="{bar:.2f}" height="12" fill="{color}"/>')
            out.append(f'<text x="{372+bar:.2f}" y="{by+11}">{row[f"{prefix}_count"]} ({value:.1f}%)</text>')
    out.append("</g></svg>")
    path.write_text("\n".join(out)+"\n", encoding="utf-8", newline="\n")


def run(output):
    (output / "local_verification.json").unlink(missing_ok=True)
    snapshot = read_json("study_snapshot.json")
    data = BASELINE.read_bytes()
    if hashlib.sha256(data).hexdigest() != snapshot["baseline_sha256"]:
        raise ValueError("Published Linux snapshot hash differs from the frozen study input")
    with (ROOT / "decisions.csv").open(encoding="utf-8-sig", newline="") as stream:
        decision_rows = list(csv.DictReader(stream))
    decisions = {(r["source"], r["id"]): r for r in decision_rows}
    if len(decisions) != len(decision_rows):
        raise ValueError("Duplicate review keys")
    report_links = read_json("report_links.json")["reports"]
    if set(report_links) != {r["Bug ID"] for r in snapshot["downstream"]}:
        raise ValueError("Incomplete downstream report link audit")
    ledger = audit(snapshot, json.loads(data), decisions, read_json("patch_evidence.json"), report_links)
    included = [r for r in ledger if r["decision"] == "include"]
    borderline = [r for r in ledger if r["decision"] == "borderline"]
    comparisons = list(compare(included, borderline))
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "candidate_audit.csv", ledger)
    write_csv(output / "defects.csv", included)
    review_queue = []
    for row in included + borderline:
        changed = [field for field in FIELDS if row["source"] == "LP"
                   and row[field] != row[f"author_{field}"]]
        reasons = []
        if changed:
            reasons.append("Published labels differ: " + ", ".join(changed))
        if not row["comparable_direct_diff"]:
            reasons.append("Packaging diff; published size used")
        if row["decision"] == "borderline":
            reasons.append("Product versus test-only scope")
        if any(row[field] == "Unknown" for field in FIELDS):
            reasons.append("Uncertain category")
        if reasons:
            review_queue.append(dict(source=row["source"], defect_id=row["defect_id"],
                                     issue_url=row["issue_url"], fix_url=row["fix_url"],
                                     layer=row["layer"], author_layer=row["author_layer"],
                                     evidence=row["decision_evidence"], review_reason=" | ".join(reasons),
                                     reviewer="", adjudication="pending"))
    if review_queue:
        write_csv(output / "peer_review_queue.csv", review_queue)
    write_csv(output / "distribution.csv", comparisons)
    write_csv(output / "spearman.csv", list(rank_comparison(included, borderline)))
    flow = Counter((r["source"], r["decision"], r["decision_evidence"] if r["decision"] == "exclude" else "Eligible")
                   for r in ledger)
    write_csv(output / "screening_flow.csv", [
        dict(source=src, decision=decision, reason=reason, count=count)
        for (src, decision, reason), count in sorted(flow.items())
    ])
    gap_rows = []
    for scope, layer, rows in scopes(included, borderline):
        if scope not in {"all", "same_layer", "same_layer_author_labels", "direct_diff", "include_borderline_test"}:
            continue
        if scope.startswith("same_layer") and layer != "System Service Layer":
            continue
        groups = [[r["trigger"] for r in rows if r["source"] == src]
                  for src in SOURCES]
        if min(map(len, groups)) == 0:
            continue
        a, b = groups
        env = "Environment Dependency Trigger"
        a_min, a_max = (a.count(env) + extra * a.count("Unknown") for extra in (0, 1))
        b_min, b_max = (b.count(env) + extra * b.count("Unknown") for extra in (0, 1))
        gap_rows.append(dict(scope=scope, layer=layer, lp_n=len(a), gh_n=len(b),
                             lp_confirmed=a_min, gh_confirmed=b_min, lp_unknown=a.count("Unknown"),
                             gh_unknown=b.count("Unknown"),
                             github_minus_launchpad_low_pp=100 * (b_min/len(b) - a_max/len(a)),
                             github_minus_launchpad_high_pp=100 * (b_max/len(b) - a_min/len(a))))
    write_csv(output / "environment_sensitivity.csv", gap_rows)
    chart(output / "layers.svg", [r for r in comparisons if r["scope"] == "all" and r["dimension"] == "layer"],
          "Layer composition in the screened cohorts")
    chart(output / "service_triggers.svg", [r for r in comparisons if r["scope"] == "same_layer"
          and r["layer"] == "System Service Layer" and r["dimension"] == "trigger"],
          "System Service triggers under harmonized layer labels")
    summary = {src: dict(candidates=sum(r["source"] == src for r in ledger),
                         included=sum(r["source"] == src for r in included),
                         direct_diff=sum(r["comparable_direct_diff"] for r in included if r["source"] == src))
               for src in SOURCES}
    summary["input_sha256"] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                               for name in ("study_snapshot.json", "patch_evidence.json", "report_links.json", "decisions.csv", "analysis.py")}
    summary["baseline_sha256"] = snapshot["baseline_sha256"]
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n",
                                         encoding="utf-8", newline="\n")
    print(json.dumps(summary, sort_keys=True))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    run(parser.parse_args().out_dir)
