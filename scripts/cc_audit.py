"""
cc_audit.py
-----------
Phase 1: Common Crawl Domain Audit

Queries each ETD repository domain against five Common Crawl indexes
(2022-2024) using the CC Index API. Records URL hits, timestamps,
HTTP status codes, and MIME types.

Usage:
    python scripts/cc_audit.py
    python scripts/cc_audit.py --dry-run   # test pipeline without HTTP

Output:
    data/raw/{domain}_{index}.json   — raw API response per domain per index
    results/exposure_scores.csv      — final exposure scores (Table 1)

CC Index API docs: https://index.commoncrawl.org/
"""

import json
import time
import os
import requests
import pandas as pd
from tqdm import tqdm

# ── Constants ─────────────────────────────────────────────────────────────────

CC_INDEX_BASE = "https://index.commoncrawl.org/{index}-index"

CC_INDEXES = [
    "CC-MAIN-2022-21",
    "CC-MAIN-2022-49",
    "CC-MAIN-2023-14",
    "CC-MAIN-2023-40",
    "CC-MAIN-2024-10",
]

INSTITUTIONS_CSV = "data/institutions.csv"
RAW_DIR         = "data/raw"
RESULTS_DIR     = "results"
OUTPUT_CSV      = "results/exposure_scores.csv"

REQUEST_DELAY   = 1.5   # seconds between requests — be polite to CC servers
MAX_RETRIES     = 3
QUERY_LIMIT     = 10    # CC API caps results per query at 10


# ── Core query ────────────────────────────────────────────────────────────────

def query_cc_index(domain: str, index: str) -> dict:
    """
    Query a single CC index for a given domain.

    Exact query pattern (as documented in paper Section 3.1):
        GET https://index.commoncrawl.org/{index}-index?
            url={domain}/*&output=json&limit=10

    A domain is counted as 'present' if ≥1 URL returns HTTP status 200.

    Returns dict:
        hits     — list of raw hit objects
        count    — number of valid (status=200) hits
        present  — bool
        years    — list of years found in timestamps
        error    — exception string or None
    """
    url    = CC_INDEX_BASE.format(index=index)
    params = {"url": f"{domain}/*", "output": "json", "limit": QUERY_LIMIT}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, params=params, timeout=30)

            if resp.status_code == 404:
                # Domain genuinely absent from this index
                return {"hits": [], "count": 0, "present": False, "years": [], "error": None}

            resp.raise_for_status()

            # CC API returns newline-delimited JSON
            hits = []
            for line in resp.text.strip().splitlines():
                line = line.strip()
                if line:
                    try:
                        hits.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            valid = [h for h in hits if str(h.get("status", "")) == "200"]
            years = sorted({h["timestamp"][:4] for h in valid if "timestamp" in h})

            return {"hits": valid, "count": len(valid),
                    "present": len(valid) > 0, "years": years, "error": None}

        except Exception as exc:
            if attempt < MAX_RETRIES:
                time.sleep(REQUEST_DELAY * attempt)
            else:
                return {"hits": [], "count": 0, "present": False,
                        "years": [], "error": str(exc)}


# ── Main audit loop ───────────────────────────────────────────────────────────

def run_audit(dry_run: bool = False) -> pd.DataFrame:
    os.makedirs(RAW_DIR,     exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    institutions = pd.read_csv(INSTITUTIONS_CSV)
    records = []

    for _, row in tqdm(institutions.iterrows(), total=len(institutions),
                       desc="Auditing institutions"):
        domain      = row["domain"]
        institution = row["institution"]
        region      = row["region"]

        indexes_found = 0
        all_years     = set()
        total_hits    = 0

        for index in CC_INDEXES:
            raw_path = os.path.join(
                RAW_DIR, f"{domain.replace('/', '_').replace('.', '_')}_{index}.json"
            )

            if dry_run:
                result = {"hits": [], "count": 0, "present": False,
                          "years": [], "error": "dry_run"}
            else:
                result = query_cc_index(domain, index)
                time.sleep(REQUEST_DELAY)

            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump({"domain": domain, "index": index, "result": result}, f, indent=2)

            if result["present"]:
                indexes_found += 1
                all_years.update(result["years"])
                total_hits += result["count"]

        year_range = (f"{min(all_years)}–{max(all_years)}" if all_years else "—")

        records.append({
            "institution":      institution,
            "domain":           domain,
            "region":           region,
            "cc_indexes_found": indexes_found,
            "year_range":       year_range,
            "total_url_hits":   total_hits,
            "cc_present":       indexes_found > 0,
            "manifest_mentions": 0,       # populated by manifest_audit.py
            "exposure_score":   indexes_found * 2,  # updated after manifest step
        })

    df = pd.DataFrame(records).sort_values("exposure_score", ascending=False)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n✓ CC audit complete → {OUTPUT_CSV}")
    print(df[["institution", "region", "cc_indexes_found",
              "year_range", "exposure_score"]].to_string(index=False))
    return df


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Common Crawl ETD Domain Audit")
    p.add_argument("--dry-run", action="store_true",
                   help="Skip HTTP requests; test pipeline only")
    args = p.parse_args()
    run_audit(dry_run=args.dry_run)
