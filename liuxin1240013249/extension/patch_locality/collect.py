#!/usr/bin/env python3
"""Collect and freeze real patch diff metadata for the patch-locality extension.

This is the ONLY script in extension/patch_locality/ that accesses the network.
It produces frozen JSON snapshots in data/ so that analysis.py and unit tests
run completely offline and deterministically using only the Python stdlib.

Usage:
    python extension/patch_locality/collect.py
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

EXT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXT_DIR.parents[1]
BASELINE_DATA_DIR = PROJECT_ROOT / "data"
OUT_DATA_DIR = EXT_DIR / "data"

USER_AGENT = "cs340-os-defects-replication-patch-locality/1.0"

SIZE_BUCKETS = [
    ("1-9", 1, 10),
    ("10-29", 10, 30),
    ("30-49", 30, 50),
    ("50-99", 50, 100),
    ("100-500", 100, 501),
]

FORCED_BASELINE_IDS = {
    "android": ["A-374257207", "A-273501008", "A-280793427"],
    "linux": ["2044216", "2114712", "2097605"],
    "harmony": ["CVE-2024-50082 (CVE-2024-50046)", "CVE-2024-50038 (CVE-2024-50015)"],
}


def http_get(url: str, timeout: int = 25, accept: str | None = None) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def http_get_json(url: str, timeout: int = 25) -> object:
    raw = http_get(url, timeout=timeout, accept="application/json")
    text = raw.decode("utf-8", errors="replace")
    if text.startswith(")]}'"):
        text = text.split("\n", 1)[1]
    return json.loads(text)


def classify_file_category(filepath: str) -> str:
    """Classify a changed file path into production, test, doc, or packaging_or_generated."""
    low = filepath.lower().replace("\\", "/")
    parts = [p for p in low.split("/") if p]
    name = parts[-1] if parts else low

    if any(p in ("debian", ".pc") for p in parts) or name.endswith((".debdiff", ".dsc", ".changes")):
        return "packaging_or_generated"
    if any(p in ("generated", "gen", "third_party") for p in parts) or name.endswith(
        (".pb.cc", ".pb.h", "_pb2.py", ".generated.h", ".generated.c", ".lock")
    ) or name in ("package-lock.json", "cargo.lock", "yarn.lock"):
        return "packaging_or_generated"

    if (
        any(p in ("test", "tests", "testing", "unittest", "unittests", "androidtest", "cts", "fuzz", "fuzzer") for p in parts)
        or name.startswith("test_")
        or name.startswith("test-")
        or name.endswith(("_test.c", "_test.cc", "_test.cpp", "_test.h", "_test.py", "_test.rs", "test.java", "tests.java", "test.py"))
        or "selftests" in parts
        or "fuzzing" in parts
    ):
        return "test"

    if (
        any(p in ("doc", "docs", "documentation", "man") for p in parts)
        or name.endswith((".md", ".rst", ".txt", ".adoc"))
        or name in ("readme", "changelog", "license", "copying", "authors", "news")
    ):
        return "doc"

    return "production"


def parse_unified_diff(diff_text: str) -> list[dict]:
    """Parse per-file additions/deletions from a unified diff or git patch."""
    files = []
    cur_path = None
    adds = 0
    dels = 0

    def flush():
        nonlocal cur_path, adds, dels
        if cur_path is not None:
            files.append({
                "filepath": cur_path,
                "additions": adds,
                "deletions": dels,
                "changes": adds + dels,
                "file_category": classify_file_category(cur_path),
            })
        cur_path = None
        adds = 0
        dels = 0

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            flush()
            m = re.match(r"diff --git a/(.+?) b/(.+)$", line)
            if m:
                cur_path = m.group(2)
            continue
        if line.startswith("+++ "):
            path_part = line[4:].strip()
            if path_part == "/dev/null":
                continue
            if path_part.startswith("b/"):
                path_part = path_part[2:]
            if cur_path is None:
                cur_path = path_part
            continue
        if line.startswith("--- "):
            continue
        if cur_path is not None:
            if line.startswith("+") and not line.startswith("+++"):
                adds += 1
            elif line.startswith("-") and not line.startswith("---"):
                dels += 1

    flush()
    return files


def fetch_patch_files(url: str) -> tuple[list[dict], str, str]:
    """Fetch per-file diff stats and return (files, fetched_url, sha256)."""
    url = url.strip().split()[0]
    if "android.googlesource.com" in url:
        base = url.split("?")[0]
        raw = http_get(base + "?format=TEXT")
        text = base64.b64decode(raw).decode("utf-8", errors="replace")
        return parse_unified_diff(text), base + "?format=TEXT", hashlib.sha256(text.encode("utf-8")).hexdigest()
    if "github.com" in url and "/commit/" in url and not url.endswith((".diff", ".patch")):
        raw = http_get(url + ".diff")
        text = raw.decode("utf-8", errors="replace")
        return parse_unified_diff(text), url + ".diff", hashlib.sha256(text.encode("utf-8")).hexdigest()
    if "gitlab.freedesktop.org" in url and "/commit/" in url and not url.endswith((".diff", ".patch")):
        raw = http_get(url + ".diff")
        text = raw.decode("utf-8", errors="replace")
        return parse_unified_diff(text), url + ".diff", hashlib.sha256(text.encode("utf-8")).hexdigest()

    raw = http_get(url)
    text = raw.decode("utf-8", errors="replace")
    files = parse_unified_diff(text)
    if files:
        return files, url, hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Fallback for Gitee commit URLs whose .patch returns HTML
    m = re.match(r"https?://gitee\.com/([^/]+/[^/]+)/commit/([0-9a-fA-F]+)", url)
    if m:
        repo, sha = m.group(1), m.group(2)
        api_url = f"https://gitee.com/api/v5/repos/{repo}/commits/{sha}"
        data = http_get_json(api_url)
        files = []
        for f in data.get("files", []):
            fn = f.get("filename") or ""
            adds = int(f.get("additions", 0))
            dels = int(f.get("deletions", 0))
            files.append({
                "filepath": fn,
                "additions": adds,
                "deletions": dels,
                "changes": adds + dels,
                "file_category": classify_file_category(fn),
            })
        return files, api_url, hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

    return [], url, hashlib.sha256(text.encode("utf-8")).hexdigest()


def bucket_for(lc: int) -> str | None:
    for name, lo, hi in SIZE_BUCKETS:
        if lo <= lc < hi:
            return name
    return None


def sample_baseline_diffs(per_bucket: int = 3) -> list[dict]:
    """Sample baseline records across size buckets and fetch their real diffs."""
    out = []
    for os_tag in ("android", "linux", "harmony"):
        rows = json.loads((BASELINE_DATA_DIR / f"defects_{os_tag}.json").read_text(encoding="utf-8"))
        by_id = {r["Bug ID"]: r for r in rows}
        chosen_ids = []
        for bid in FORCED_BASELINE_IDS[os_tag]:
            if bid in by_id and bid not in chosen_ids:
                chosen_ids.append(bid)

        by_bucket: dict[str, list[dict]] = {b[0]: [] for b in SIZE_BUCKETS}
        for r in rows:
            b = bucket_for(int(r["Line Changes"]))
            if b and r["Bug ID"] not in chosen_ids:
                by_bucket[b].append(r)

        for bname, _, _ in SIZE_BUCKETS:
            pool = by_bucket[bname]
            step = max(1, len(pool) // max(1, per_bucket))
            picked = 0
            for idx in range(0, len(pool), step):
                if picked >= per_bucket:
                    break
                chosen_ids.append(pool[idx]["Bug ID"])
                picked += 1

        print(f"[baseline {os_tag}] fetching {len(chosen_ids)} diffs...")
        for bid in chosen_ids:
            r = by_id[bid]
            patch_url = (r.get("Patch") or "").strip().split()[0]
            try:
                files, fetched_url, digest = fetch_patch_files(patch_url)
                if not files:
                    print(f"  WARN empty diff parse for {os_tag} {bid} ({fetched_url})")
                    continue
                out.append({
                    "os": os_tag,
                    "bug_id": bid,
                    "patch_url": patch_url,
                    "fetched_url": fetched_url,
                    "diff_sha256": digest,
                    "paper_line_additions": int(r["Line Additions"]),
                    "paper_line_deletions": int(r["Line Deletions"]),
                    "paper_line_changes": int(r["Line Changes"]),
                    "paper_modified_files": int(r["Modified Files"]),
                    "paper_involved_functions": int(str(r["Involved Functions"]).rstrip("+")),
                    "os_layer": r["OS Layer"],
                    "affected_function": r["Affected Function"],
                    "trigger_scenario": r["Trigger Scenario"],
                    "severity": r["Severity Level"],
                    "files": files,
                })
                time.sleep(0.15)
            except Exception as e:
                print(f"  ERR {os_tag} {bid}: {e}")
    return out


def collect_systemd_html_large(limit: int = 10) -> list[dict]:
    """Collect merged systemd/systemd PRs (501-1000 lines) via web search + .diff."""
    results = []
    seen = set()
    # Seed with known 2023-2025 systemd fix PRs plus live search pages
    seed_nums = ["39390", "37271", "31550", "35401"]
    candidate_nums = list(seed_nums)
    for page in (1, 2, 3, 4):
        q = urllib.parse.quote("is:pr is:merged merged:2023-05-01..2025-12-31 fix")
        url = f"https://github.com/systemd/systemd/pulls?page={page}&q={q}"
        try:
            html = http_get(url, timeout=15).decode("utf-8", errors="replace")
            candidate_nums.extend(re.findall(r"/systemd/systemd/pull/(\d+)", html))
        except Exception:
            break
    for num in candidate_nums:
        if num in seen:
            continue
        seen.add(num)
        if len(seen) > 65:
            break
        diff_url = f"https://github.com/systemd/systemd/pull/{num}.diff"
        try:
            text = http_get(diff_url, timeout=12).decode("utf-8", errors="replace")
        except Exception:
            continue
        files = parse_unified_diff(text)
        adds = sum(f["additions"] for f in files)
        dels = sum(f["deletions"] for f in files)
        tot = adds + dels
        if 501 <= tot <= 1000:
            pr_html = http_get(f"https://github.com/systemd/systemd/pull/{num}", timeout=12).decode("utf-8", errors="replace")
            m_title = re.search(r"<title>(.+?)\s*·\s*Pull Request", pr_html, re.S)
            title = m_title.group(1).strip() if m_title else f"systemd PR #{num}"
            m_date = re.search(r'datetime="(\d{4}-\d{2}-\d{2}T[^"]+)"', pr_html)
            merged_at = m_date.group(1) if m_date else ""
            results.append({
                "os": "Linux",
                "repo": "systemd/systemd",
                "source": "GitHub_PR",
                "candidate_id": f"GH-systemd-{num}",
                "defect_id": str(num),
                "title": title,
                "body_excerpt": "",
                "original_url": f"https://github.com/systemd/systemd/pull/{num}",
                "patch_url": diff_url,
                "date": merged_at,
                "date_type": "github_merged_at",
                "raw_lines_added": adds,
                "raw_lines_deleted": dels,
                "raw_lines_changed": tot,
                "raw_files_changed": len(files),
                "files": files,
            })
            print(f"  [systemd] #{num}: +{adds}/-{dels} ({tot} lines, {len(files)} files) | {title[:60]}", flush=True)
            if len(results) >= limit:
                return results
    return results


def collect_kernel_cgit_large(limit: int = 8) -> list[dict]:
    """Collect Linux kernel commits with Fixes: tag and 501-1000 lines from git.kernel.org."""
    results = []
    seen = set()
    url = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/?qt=grep&q=Fixes%3A&ofs=0"
    try:
        html = http_get(url, timeout=15).decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [linux-kernel] list ERR: {e}", flush=True)
        return results
    shas = re.findall(r"commit/\?id=([0-9a-f]{40})", html)
    for sha in shas[:30]:
        if sha in seen:
            continue
        seen.add(sha)
        # First check lightweight commit summary page for diffstat total lines
        c_url = f"https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id={sha}"
        try:
            c_html = http_get(c_url, timeout=10).decode("utf-8", errors="replace")
        except Exception:
            continue
        m_stat = re.search(r"(\d+)\s+files?\s+changed,\s+(\d+)\s+insertions?\(\+\)(?:,\s+(\d+)\s+deletions?\(-\))?", c_html)
        if not m_stat:
            m_stat2 = re.search(r"(\d+)\s+files?\s+changed,\s+(\d+)\s+deletions?\(-\)", c_html)
            tot_est = int(m_stat2.group(2)) if m_stat2 else 0
        else:
            tot_est = int(m_stat.group(2)) + int(m_stat.group(3) or 0)
        if not (501 <= tot_est <= 1000):
            continue
        patch_url = f"https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/patch/?id={sha}"
        try:
            text = http_get(patch_url, timeout=15).decode("utf-8", errors="replace")
        except Exception:
            continue
        files = parse_unified_diff(text)
        adds = sum(f["additions"] for f in files)
        dels = sum(f["deletions"] for f in files)
        tot = adds + dels
        if 501 <= tot <= 1000:
            m_subj = re.search(r"^Subject:\s*(?:\[PATCH[^\]]*\]\s*)?(.+)$", text, re.M)
            m_date = re.search(r"^Date:\s*(.+)$", text, re.M)
            title = m_subj.group(1).strip() if m_subj else sha[:12]
            results.append({
                "os": "Linux",
                "repo": "torvalds/linux",
                "source": "Kernel_Git",
                "candidate_id": f"Kernel-{sha[:10]}",
                "defect_id": sha[:12],
                "title": title,
                "body_excerpt": text[:500],
                "original_url": c_url,
                "patch_url": patch_url,
                "date": m_date.group(1).strip() if m_date else "",
                "date_type": "git_commit_date",
                "raw_lines_added": adds,
                "raw_lines_deleted": dels,
                "raw_lines_changed": tot,
                "raw_files_changed": len(files),
                "files": files,
            })
            print(f"  [linux-kernel] {sha[:10]}: +{adds}/-{dels} ({tot} lines, {len(files)} files) | {title[:60]}", flush=True)
            if len(results) >= limit:
                return results
    return results


def collect_gitee_harmony_large(limit: int = 12) -> list[dict]:
    """Collect merged PRs in OpenHarmony repos with 501-1000 changed lines."""
    repos = [
        "openharmony/kernel_liteos_a",
        "openharmony/communication_dsoftbus",
        "openharmony/security_huks",
        "openharmony/arkui_ace_engine",
        "openharmony/graphic_graphic_2d",
    ]
    results = []
    for repo in repos:
        for page in (1, 2, 3):
            url = f"https://gitee.com/api/v5/repos/{repo}/pulls?state=merged&sort=updated&direction=desc&page={page}&per_page=40"
            try:
                prs = http_get_json(url)
            except Exception as e:
                print(f"  [gitee {repo}] ERR: {e}")
                break
            if not isinstance(prs, list) or not prs:
                break
            for pr in prs:
                title = pr.get("title") or ""
                body = pr.get("body") or ""
                low = (title + " " + body).lower()
                if not any(k in low for k in ("fix", "bug", "cve", "修复", "缺陷", "漏洞", "问题", "crash", "leak", "overflow", "null")):
                    continue
                num = pr["number"]
                patch_url = f"https://gitee.com/{repo}/pulls/{num}.patch"
                try:
                    text = http_get(patch_url).decode("utf-8", errors="replace")
                except Exception:
                    continue
                files = parse_unified_diff(text)
                adds = sum(f["additions"] for f in files)
                dels = sum(f["deletions"] for f in files)
                tot = adds + dels
                if 501 <= tot <= 1000:
                    results.append({
                        "os": "HarmonyOS",
                        "repo": repo,
                        "source": "Gitee_PR",
                        "candidate_id": f"Gitee-{repo.split('/')[1]}-{num}",
                        "defect_id": f"{repo.split('/')[1]}#{num}",
                        "title": title,
                        "body_excerpt": body[:400],
                        "original_url": pr.get("html_url", ""),
                        "patch_url": patch_url,
                        "date": pr.get("merged_at") or pr.get("updated_at") or "",
                        "date_type": "gitee_merged_at",
                        "raw_lines_added": adds,
                        "raw_lines_deleted": dels,
                        "raw_lines_changed": tot,
                        "raw_files_changed": len(files),
                        "files": files,
                    })
                    print(f"  [harmony {repo}] #{num}: +{adds}/-{dels} ({tot} lines, {len(files)} files) | {title[:60]}", flush=True)
                    if len(results) >= limit:
                        return results
                time.sleep(0.05)
    return results


def collect_android_large(limit: int = 8) -> list[dict]:
    """Collect AOSP bugfix commits with 501-1000 changed lines from Gitiles."""
    repos = [
        "platform/frameworks/base",
        "platform/packages/modules/Bluetooth",
        "platform/packages/modules/Connectivity",
    ]
    results = []
    for repo in repos:
        url = f"https://android.googlesource.com/{repo}/+log/main?n=40&format=JSON"
        try:
            data = http_get_json(url)
        except Exception as e:
            print(f"  [android {repo}] ERR: {e}")
            continue
        commits = data.get("log", [])
        for c in commits:
            msg = c.get("message", "")
            low = msg.lower()
            if not any(k in low for k in ("fix", "bug:", "crash", "leak", "npe", "null", "cve")):
                continue
            sha = c["commit"]
            patch_url = f"https://android.googlesource.com/{repo}/+/{sha}%5E%21/"
            try:
                files, _, _ = fetch_patch_files(patch_url)
            except Exception:
                continue
            adds = sum(f["additions"] for f in files)
            dels = sum(f["deletions"] for f in files)
            tot = adds + dels
            if 501 <= tot <= 1000:
                m_bug = re.search(r"Bug:\s*(\d+)", msg)
                defect_id = f"A-{m_bug.group(1)}" if m_bug else f"AOSP-{sha[:10]}"
                title = msg.splitlines()[0] if msg else sha[:10]
                results.append({
                    "os": "Android",
                    "repo": repo,
                    "source": "AOSP_Gitiles",
                    "candidate_id": f"AOSP-{repo.split('/')[-1]}-{sha[:10]}",
                    "defect_id": defect_id,
                    "title": title,
                    "body_excerpt": msg[:400],
                    "original_url": patch_url,
                    "patch_url": patch_url,
                    "date": c.get("committer", {}).get("time", ""),
                    "date_type": "git_commit_date",
                    "raw_lines_added": adds,
                    "raw_lines_deleted": dels,
                    "raw_lines_changed": tot,
                    "raw_files_changed": len(files),
                    "files": files,
                })
                print(f"  [android {repo}] {sha[:10]}: +{adds}/-{dels} ({tot} lines, {len(files)} files) | {title[:60]}", flush=True)
                if len(results) >= limit:
                    return results
            time.sleep(0.05)
    return results


def collect_targeted_large(existing: list[dict]) -> list[dict]:
    """Targeted collection of bugfix-titled 501-1000 line patches across OSes."""
    cands = list(existing)
    seen_ids = {c["candidate_id"] for c in cands}

    def add_cand(c: dict) -> None:
        if c["candidate_id"] not in seen_ids:
            seen_ids.add(c["candidate_id"])
            cands.append(c)

    print("=== Targeted systemd bugfix PRs ===", flush=True)
    systemd_got = 0
    for page in (1, 2, 3):
        q = urllib.parse.quote("is:pr is:merged in:title fix merged:2023-05-01..2025-12-31")
        url = f"https://github.com/systemd/systemd/pulls?page={page}&q={q}"
        try:
            html = http_get(url, timeout=15).decode("utf-8", errors="replace")
        except Exception:
            break
        for num in dict.fromkeys(re.findall(r"/systemd/systemd/pull/(\d+)", html)):
            cid = f"GH-systemd-{num}"
            if cid in seen_ids:
                continue
            try:
                text = http_get(f"https://github.com/systemd/systemd/pull/{num}.diff", timeout=12).decode("utf-8", errors="replace")
            except Exception:
                continue
            files = parse_unified_diff(text)
            adds = sum(f["additions"] for f in files)
            dels = sum(f["deletions"] for f in files)
            tot = adds + dels
            if 501 <= tot <= 1000:
                pr_html = http_get(f"https://github.com/systemd/systemd/pull/{num}", timeout=12).decode("utf-8", errors="replace")
                m_title = re.search(r"<title>(.+?)\s*·\s*Pull Request", pr_html, re.S)
                title = m_title.group(1).strip() if m_title else f"systemd PR #{num}"
                m_date = re.search(r'datetime="(\d{4}-\d{2}-\d{2}T[^"]+)"', pr_html)
                merged_at = m_date.group(1) if m_date else ""
                add_cand({
                    "os": "Linux", "repo": "systemd/systemd", "source": "GitHub_PR",
                    "candidate_id": cid, "defect_id": str(num), "title": title,
                    "body_excerpt": "", "original_url": f"https://github.com/systemd/systemd/pull/{num}",
                    "patch_url": f"https://github.com/systemd/systemd/pull/{num}.diff",
                    "date": merged_at, "date_type": "github_merged_at",
                    "raw_lines_added": adds, "raw_lines_deleted": dels,
                    "raw_lines_changed": tot, "raw_files_changed": len(files), "files": files,
                })
                systemd_got += 1
                print(f"  [systemd] #{num}: +{adds}/-{dels} ({tot}L, {len(files)}F) | {title[:65]}", flush=True)
                if systemd_got >= 6:
                    break
        if systemd_got >= 6:
            break

    print("=== Targeted HarmonyOS bugfix PRs ===", flush=True)
    harm_got = 0
    for repo in ("openharmony/kernel_liteos_a", "openharmony/security_huks", "openharmony/arkui_ace_engine", "openharmony/graphic_graphic_2d"):
        for page in (1, 2, 3, 4):
            try:
                prs = http_get_json(f"https://gitee.com/api/v5/repos/{repo}/pulls?state=merged&sort=updated&direction=desc&page={page}&per_page=50", timeout=15)
            except Exception:
                break
            if not isinstance(prs, list) or not prs:
                break
            for pr in prs:
                title = pr.get("title") or ""
                low = title.lower()
                if any(bad in low for bad in ("unittest", "fuzz", "testcase", "delete code", "format", "clean", "dts", "cherry")):
                    continue
                if not any(good in low for good in ("fix", "bug", "cve", "修复", "解决", "crash", "leak", "null", "越界", "空指针")):
                    continue
                num = pr["number"]
                cid = f"Gitee-{repo.split('/')[1]}-{num}"
                if cid in seen_ids:
                    continue
                patch_url = f"https://gitee.com/{repo}/pulls/{num}.patch"
                try:
                    text = http_get(patch_url, timeout=15).decode("utf-8", errors="replace")
                except Exception:
                    continue
                files = parse_unified_diff(text)
                adds = sum(f["additions"] for f in files)
                dels = sum(f["deletions"] for f in files)
                tot = adds + dels
                if 501 <= tot <= 1000:
                    add_cand({
                        "os": "HarmonyOS", "repo": repo, "source": "Gitee_PR",
                        "candidate_id": cid, "defect_id": f"{repo.split('/')[1]}#{num}",
                        "title": title, "body_excerpt": (pr.get("body") or "")[:400],
                        "original_url": pr.get("html_url", ""), "patch_url": patch_url,
                        "date": pr.get("merged_at") or pr.get("updated_at") or "",
                        "date_type": "gitee_merged_at",
                        "raw_lines_added": adds, "raw_lines_deleted": dels,
                        "raw_lines_changed": tot, "raw_files_changed": len(files), "files": files,
                    })
                    harm_got += 1
                    print(f"  [harmony {repo}] #{num}: +{adds}/-{dels} ({tot}L, {len(files)}F) | {title[:65]}", flush=True)
                    if harm_got >= 6:
                        break
            if harm_got >= 6:
                break
        if harm_got >= 6:
            break

    print("=== Targeted Android bugfix commits ===", flush=True)
    and_got = 0
    for repo in ("platform/frameworks/base", "platform/frameworks/av", "platform/system/core", "platform/packages/modules/Bluetooth"):
        try:
            data = http_get_json(f"https://android.googlesource.com/{repo}/+log/main?n=80&format=JSON", timeout=15)
        except Exception:
            continue
        for c in data.get("log", []):
            msg = c.get("message", "")
            title = msg.splitlines()[0] if msg else ""
            low = title.lower()
            if any(bad in low for bad in ("merge ", "convert ", "optimize", "clean up", "cleanup", "refactor", "rename")):
                continue
            if not any(good in low for good in ("fix", "prevent", "resolve", "null", "leak", "crash", "guard", "avoid")):
                continue
            sha = c["commit"]
            cid = f"AOSP-{repo.split('/')[-1]}-{sha[:10]}"
            if cid in seen_ids:
                continue
            patch_url = f"https://android.googlesource.com/{repo}/+/{sha}%5E%21/"
            try:
                files, _, _ = fetch_patch_files(patch_url)
            except Exception:
                continue
            adds = sum(f["additions"] for f in files)
            dels = sum(f["deletions"] for f in files)
            tot = adds + dels
            if 501 <= tot <= 1000:
                m_bug = re.search(r"Bug:\s*(\d+)", msg)
                defect_id = f"A-{m_bug.group(1)}" if m_bug else f"AOSP-{sha[:10]}"
                add_cand({
                    "os": "Android", "repo": repo, "source": "AOSP_Gitiles",
                    "candidate_id": cid, "defect_id": defect_id, "title": title,
                    "body_excerpt": msg[:400], "original_url": patch_url, "patch_url": patch_url,
                    "date": c.get("committer", {}).get("time", ""), "date_type": "git_commit_date",
                    "raw_lines_added": adds, "raw_lines_deleted": dels,
                    "raw_lines_changed": tot, "raw_files_changed": len(files), "files": files,
                })
                and_got += 1
                print(f"  [android {repo}] {sha[:10]}: +{adds}/-{dels} ({tot}L, {len(files)}F) | {title[:65]}", flush=True)
                if and_got >= 5:
                    break
        if and_got >= 5:
            break

    return cands


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-baseline", action="store_true")
    parser.add_argument("--targeted", action="store_true")
    args = parser.parse_args()

    OUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    baseline_path = OUT_DATA_DIR / "baseline_diff_sample.json"
    if (args.skip_baseline or args.targeted) and baseline_path.exists():
        baseline_samples = json.loads(baseline_path.read_text(encoding="utf-8"))
        print(f"Reusing {len(baseline_samples)} baseline diff samples from {baseline_path}", flush=True)
    else:
        print("=== Step 1: Sampling baseline diffs ===", flush=True)
        baseline_samples = sample_baseline_diffs(per_bucket=3)
        baseline_path.write_bytes(json.dumps(baseline_samples, indent=2, ensure_ascii=False).encode("utf-8"))
        print(f"Saved {len(baseline_samples)} baseline diff samples -> {baseline_path}", flush=True)

    cand_path = OUT_DATA_DIR / "large_patch_candidates.json"
    if args.targeted:
        existing = json.loads(cand_path.read_text(encoding="utf-8")) if cand_path.exists() else []
        candidates = collect_targeted_large(existing)
    else:
        print("\n=== Step 2: Collecting 501-1000 line candidates ===", flush=True)
        candidates = []
        print("Collecting systemd...", flush=True)
        candidates.extend(collect_systemd_html_large(limit=8))
        print(f"  systemd done: {len(candidates)}", flush=True)
        print("Collecting linux kernel...", flush=True)
        candidates.extend(collect_kernel_cgit_large(limit=8))
        print(f"  total after linux kernel: {len(candidates)}", flush=True)
        print("Collecting harmonyos...", flush=True)
        candidates.extend(collect_gitee_harmony_large(limit=8))
        print(f"  total after harmonyos: {len(candidates)}", flush=True)
        print("Collecting android...", flush=True)
        candidates.extend(collect_android_large(limit=8))
    cand_path.write_bytes(json.dumps(candidates, indent=2, ensure_ascii=False).encode("utf-8"))
    print(f"Saved {len(candidates)} large patch candidates -> {cand_path}", flush=True)

    prov = {
        "collected_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "baseline_sample_count": len(baseline_samples),
        "large_candidate_count": len(candidates),
        "files": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(OUT_DATA_DIR.iterdir())
            if p.is_file() and p.name != "PROVENANCE.json"
        },
    }
    prov_path = OUT_DATA_DIR / "PROVENANCE.json"
    prov_path.write_bytes(json.dumps(prov, indent=2).encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
