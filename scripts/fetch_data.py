#!/usr/bin/env python3
"""Fetch the publicly released defect dataset and store a local snapshot.

The authors publish the 1,500 labelled defect records through a browser
dashboard at https://zuohongyao.github.io/ .  The dashboard embeds the complete
dataset in its HTML as a JavaScript object::

    var DATA = {
      android: [ {...}, ... ],
      harmony: [ {...}, ... ],
      linux:   [ {...}, ... ],
      datasets: [ ... chart configuration, ignored ... ]
    };

This script downloads the page, extracts the three arrays with the standard
library only, writes ``data/defects_<system>.json`` and records the SHA-256 of
the downloaded page and of every output file in ``data/PROVENANCE.json``.

Usage
-----
    python scripts/fetch_data.py                # download and refresh data/
    python scripts/fetch_data.py --check        # verify data/ against PROVENANCE
    python scripts/fetch_data.py --verify-remote  # also compare with the live page
    python scripts/fetch_data.py --snapshot page.html  # parse a saved copy
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402  (local module, path set above)

DEFAULT_URL = "https://zuohongyao.github.io/"
SYSTEM_KEYS = ("android", "harmony", "linux")
USER_AGENT = "Mozilla/5.0 (compatible; CS340-replication/1.0)"
EXPECTED_RECORDS = 500


def download(url: str, timeout: int = 120) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def extract_data(html: str) -> dict:
    """Parse the three defect arrays out of the dashboard's embedded DATA object."""
    marker = "var DATA = {"
    start = html.find(marker)
    if start < 0:
        raise ValueError("dashboard layout changed: 'var DATA = {' not found")
    segment = html[start + len("var DATA = "):]
    decoder = json.JSONDecoder()
    data = {}
    for match in re.finditer(r"([A-Za-z_]\w*)\s*:\s*\[", segment):
        key = match.group(1)
        if key not in SYSTEM_KEYS:
            continue
        array_start = segment.index("[", match.start())
        try:
            array, _ = decoder.raw_decode(segment[array_start:])
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise ValueError(f"could not parse DATA['{key}']: {exc}") from exc
        data[key] = array
    missing = [key for key in SYSTEM_KEYS if key not in data]
    if missing:
        raise ValueError(f"dashboard layout changed: missing arrays {missing}")
    return data


def verify_records(data: dict) -> None:
    fields = set()
    for key in SYSTEM_KEYS:
        rows = data[key]
        if len(rows) != EXPECTED_RECORDS:
            raise ValueError(f"{key}: expected {EXPECTED_RECORDS} records, found {len(rows)}")
        ids = [row.get("Bug ID") for row in rows]
        if len(set(ids)) != len(ids):
            raise ValueError(f"{key}: duplicate Bug IDs in downloaded data")
        for row in rows:
            for field in common.REQUIRED_FIELDS:
                if field not in row or row[field] in (None, ""):
                    raise ValueError(f"{key}: record without {field!r}: {row.get('Bug ID')}")
            fields.update(row)
    print(f"  records: " + ", ".join(f"{key}={len(data[key])}" for key in SYSTEM_KEYS))
    print(f"  fields : {len(fields)} -> {sorted(fields)}")


def write_snapshot(data: dict, source_bytes: bytes, source_url: str, data_dir: Path) -> dict:
    data_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for key in SYSTEM_KEYS:
        text = json.dumps(data[key], ensure_ascii=False, indent=1) + "\n"
        path = data_dir / f"defects_{key}.json"
        common.write_text(path, text)
        files[path.name] = {
            "sha256": common.sha256_text(text),
            "bytes": len(text.encode("utf-8")),
            "records": len(data[key]),
            "unique_bug_ids": len({row["Bug ID"] for row in data[key]}),
            "first_bug_id": data[key][0].get("Bug ID"),
            "last_bug_id": data[key][-1].get("Bug ID"),
        }
    provenance = {
        "dataset": "Public defect records released with 'Toward Understanding Operating System Defects' (arXiv:2608.20643v1)",
        "source_url": source_url,
        "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_bytes": len(source_bytes),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "extraction_method": "regex over the embedded `var DATA = {...}` object + json.JSONDecoder",
        "files": files,
    }
    common.write_text(
        data_dir / "PROVENANCE.json",
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
    )
    return provenance


def read_provenance(data_dir: Path) -> dict:
    path = data_dir / "PROVENANCE.json"
    if not path.exists():
        raise SystemExit(f"missing {path}; run `python scripts/fetch_data.py` first")
    return json.loads(path.read_text(encoding="utf-8"))


def check_local(data_dir: Path) -> int:
    provenance = read_provenance(data_dir)
    failures = 0
    for name, expected in provenance["files"].items():
        path = data_dir / name
        if not path.exists():
            print(f"  MISSING {name}")
            failures += 1
            continue
        actual = common.sha256_file(path)
        status = "ok" if actual == expected["sha256"] else "SHA-256 MISMATCH"
        failures += 0 if actual == expected["sha256"] else 1
        print(f"  {name}: {status} ({expected['records']} records)")
    if failures:
        print("dataset check FAILED; re-run `python scripts/fetch_data.py` to refresh")
        return 1
    print("dataset check passed: committed snapshot matches data/PROVENANCE.json")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default=DEFAULT_URL, help="dashboard URL (default: %(default)s)")
    parser.add_argument("--data-dir", default=str(common.DEFAULT_DATA_DIR), help="output directory")
    parser.add_argument("--snapshot", help="parse this saved HTML file instead of downloading")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--check", action="store_true", help="verify data/ against PROVENANCE.json")
    parser.add_argument("--verify-remote", action="store_true",
                        help="with --check, also compare the committed snapshot with the live page")
    args = parser.parse_args(argv)
    data_dir = Path(args.data_dir)

    if args.check:
        print("checking committed dataset snapshot...")
        code = check_local(data_dir)
        if args.verify_remote:
            provenance = read_provenance(data_dir)
            print("downloading live dashboard for comparison...")
            try:
                live = download(args.url, args.timeout)
            except Exception as exc:  # network is optional for offline reproduction
                print(f"  remote check skipped: {exc}")
                return code
            live_hash = hashlib.sha256(live).hexdigest()
            recorded = provenance["source_sha256"]
            if live_hash == recorded:
                print("  live dashboard: identical to recorded source")
            else:
                print("  live dashboard: CHANGED since the recorded snapshot")
                print(f"    recorded: {recorded}")
                print(f"    live    : {live_hash}")
                print("    (re-run fetch_data.py to refresh data/ and PROVENANCE.json)")
                code = 1
        return code

    if args.snapshot:
        print(f"reading saved dashboard snapshot: {args.snapshot}")
        raw = Path(args.snapshot).read_bytes()
        source_url = f"file://{Path(args.snapshot).resolve()}"
    else:
        print(f"downloading dashboard: {args.url}")
        raw = download(args.url, args.timeout)
        source_url = args.url
        print(f"  downloaded {len(raw)} bytes")

    data = extract_data(raw.decode("utf-8", errors="ignore"))
    print("validating extracted records...")
    verify_records(data)
    provenance = write_snapshot(data, raw, source_url, data_dir)
    print(f"wrote {len(provenance['files'])} dataset files and data/PROVENANCE.json")
    print(f"source sha256: {provenance['source_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
