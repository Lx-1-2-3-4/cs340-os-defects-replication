"""Summarize public patch metadata without storing patch bodies."""
import concurrent.futures
import hashlib
import json
import re
from pathlib import Path

from collect import HOME_DIR, fetch_bytes

def inspect(entry):
    for url in dict.fromkeys([entry["url"], *entry.get("alternates", [])]):
        try:
            raw = fetch_bytes(url)
            body = raw.decode("utf-8", errors="replace")
            sections = re.split(r"(?m)(?=^diff --git )", body)
            direct = all(s.startswith("diff --git ") for s in sections[1:]) and len(sections) > 1
            adds = deletes = 0
            in_hunk = False
            paths = []
            for line in body.splitlines():
                if line.startswith("diff --git "):
                    in_hunk = False
                    paths.append(line.partition(" b/")[2])
                elif line.startswith("@@ "):
                    in_hunk = True
                elif in_hunk and line.startswith("+"):
                    adds += 1
                elif in_hunk and line.startswith("-"):
                    deletes += 1
                elif in_hunk and not line.startswith((" ", "\\")):
                    in_hunk = False
            if not re.search(r"(?m)^@@ ", body):
                raise ValueError("Response has no text diff hunks")
            lp = re.findall(r"(?i)(?:launchpad\.net/(?:[^ \n]*/\+bug/|bugs/)|\bLP:\s*#|\blp)(\d{5,})", body)
            gh = re.findall(r"github\.com/systemd/systemd/(?:issues|pull)/(\d+)", body)
            shas = re.findall(r"(?i)\b[a-f0-9]{40}\b", body)
            return dict(entry, fetched_url=url, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                        paths=sorted(set(paths)), direct_git_diff=direct,
                        additions=adds, deletions=deletes, linked_lp_ids=sorted(set(lp)),
                        linked_gh_ids=sorted(set(gh)), commit_refs=sorted(set(shas)),
                        changed_headers=[line[:200] for line in body.splitlines()
                                         if line.startswith(("--- ", "+++ "))][:40])
        except (OSError, ValueError) as error:
            entry.setdefault("errors", []).append(dict(url=url, error=str(error)))
    return entry

def collect_evidence(snapshot):
    jobs = []
    for row in snapshot["upstream"]:
        issue = row.get("issue") or {}
        if (row.get("merged_at") and issue.get("created_at", "")[:10] >= "2023-05-01"
                and row["additions"] + row["deletions"] <= 500):
            n = row["number"]
            jobs.append(dict(source="GH", id=str(n), url=row["html_url"]+".diff",
                             alternates=[f"https://patch-diff.githubusercontent.com/raw/systemd/systemd/pull/{n}.diff"]))
    for row in snapshot["downstream"]:
        for url in row["Patch"].split():
            jobs.append(dict(source="LP", id=row["Bug ID"], url=url+".diff" if "/commit/" in url else url))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        return list(pool.map(inspect, jobs))

if __name__ == "__main__":
    snapshot = json.loads((HOME_DIR/"study_snapshot.json").read_text(encoding="utf-8"))
    print(json.dumps(collect_evidence(snapshot), indent=2, ensure_ascii=False))
