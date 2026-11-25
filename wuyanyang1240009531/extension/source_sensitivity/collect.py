"""Public metadata collector. Run analysis.py on the frozen snapshot for replay."""
from pathlib import Path
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
import re
import urllib.parse
import urllib.request

HOME_DIR = Path(__file__).resolve().parent
BASELINE = HOME_DIR.parents[2] / "liuxin1240013249/data/defects_linux.json"
WINDOW = "2023-05-01..2025-06-30"
PERIODS = ("2023-05-01..2023-12-31", "2024-01-01..2024-06-30",
           "2024-07-01..2024-12-31", "2025-01-01..2025-06-30")
GH = "https://api.github.com/repos/systemd/systemd/"
LP = "https://api.launchpad.net/1.0/"
REFS = re.compile(r"(?im)\b(?:fixes|closes|resolves)\s+(?:https://github\.com/systemd/systemd/issues/|#)(\d+)\b")
REPORT_LINKS = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:issues|pull)/\d+")

def fetch_bytes(url):
    request = urllib.request.Request(url, headers={"User-Agent": "CS340-systemd-source-study"})
    with urllib.request.urlopen(request, timeout=12) as response:
        body = response.read(2_000_001)
    if len(body) > 2_000_000:
        raise ValueError("Response exceeds study byte limit")
    return body

def get(url):
    return json.loads(fetch_bytes(url))

def pick(row, fields):
    return {key: row.get(key) for key in fields.split()}

def upstream(row):
    number = row["number"]
    detail = get(f"{GH}pulls/{number}")
    row.update(pick(detail, "merged_at merge_commit_sha additions deletions changed_files"))
    issue = get(f"{GH}issues/{row['issue_refs'][0]}")
    row["issue"] = pick(issue, "number title html_url created_at closed_at state labels pull_request")
    row["issue"]["labels"] = [item["name"] for item in issue["labels"]]
    return row

def downstream(record):
    number = record["Bug ID"]
    task_url = f"{LP}ubuntu/+source/systemd/+bug/{number}"
    task = get(task_url)
    bug = get(f"{LP}bugs/{number}")
    return dict(record, task_url=task_url, **pick(task, "status date_fix_released importance"),
                **pick(bug, "title date_created"))


def collect_report_links(snapshot):
    reports = {}
    for row in snapshot["downstream"]:
        bug_id = row["Bug ID"]
        url = f"{LP}bugs/{bug_id}"
        body = get(url).get("description") or ""
        reports[bug_id] = dict(url=url, github_report_links=sorted(set(REPORT_LINKS.findall(body))))
    return dict(retrieved_utc=datetime.now(timezone.utc).isoformat(), reports=reports)

def collect():
    queries, candidates = [], []
    for period in PERIODS:
        query = f'repo:systemd/systemd is:pr is:merged merged:{period} "Fixes #" in:body'
        url = "https://api.github.com/search/issues?" + urllib.parse.urlencode(
            dict(q=query, sort="created", order="asc", per_page=12))
        result = get(url)
        if result["incomplete_results"]:
            raise RuntimeError(f"Incomplete search response: {url}")
        queries.append(dict(period=period, url=url, search_hits=result["total_count"]))
        for item in result["items"]:
            refs = sorted(set(map(int, REFS.findall(item.get("body") or ""))))
            row = dict(pick(item, "number title html_url created_at"), issue_refs=refs, period=period)
            candidates.append(row)
    records = json.loads(BASELINE.read_text(encoding="utf-8"))
    selected = [r for r in records if re.search(r"(?:github\.com/systemd/systemd/|/\+source/systemd/)", r["Patch"])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        down = list(pool.map(downstream, selected))
        enriched = list(pool.map(upstream, [r for r in candidates if len(r["issue_refs"]) == 1]))
    replacements = {r["number"]: r for r in enriched}
    return dict(retrieved_utc=datetime.now(timezone.utc).isoformat(), queries=queries,
                baseline_sha256=hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
                upstream=[replacements.get(r["number"], r) for r in candidates], downstream=down)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-links", type=Path, metavar="SNAPSHOT",
                        help="extract Launchpad report references for a saved candidate snapshot")
    args = parser.parse_args()
    result = collect_report_links(json.loads(args.report_links.read_text(encoding="utf-8-sig"))) if args.report_links else collect()
    print(json.dumps(result, ensure_ascii=False, indent=2))
