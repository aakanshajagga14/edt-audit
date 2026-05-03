"""
license_audit.py
----------------
Phase 3: Licensing Gap Analysis

For each audited institution, records the stated license type from
ETD submission pages and repository metadata. Operationalises the
'licensing gap' as: license neither explicitly permits NOR explicitly
prohibits AI training use.

Usage:
    python scripts/license_audit.py

Output:
    results/license_gap.csv   — per-institution licensing classification
"""

import os
import pandas as pd

INSTITUTIONS_CSV = "data/institutions.csv"
OUTPUT_CSV       = "results/license_gap.csv"

# ── Manually verified license data (as of Jan 2026) ──────────────────────────
# Source: each institution's ETD submission page and repository metadata.
# Verified by visiting submission guidelines pages; URLs noted per entry.

LICENSE_DATA = [
    {
        "institution":      "IISc Bangalore",
        "license_type":     "CC-BY",
        "license_detail":   "CC-BY 4.0 — stated on ETD submission form",
        "ai_use_explicit":  False,
        "ai_permitted":     None,   # None = gap (neither permitted nor prohibited)
        "gap":              True,
        "source_url":       "https://etd.iisc.ac.in/handle/2005/submit",
        "notes":            "CC-BY does not address AI training use",
    },
    {
        "institution":      "Shodhganga",
        "license_type":     "CC-BY-NC",
        "license_detail":   "CC-BY-NC 4.0 — INFLIBNET submission policy",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://shodhganga.inflibnet.ac.in/aboutshodhganga.jsp",
        "notes":            "Non-commercial clause; AI training use unaddressed",
    },
    {
        "institution":      "IIT Delhi",
        "license_type":     "Institutional",
        "license_detail":   "IIT Delhi thesis deposit agreement; no CC license stated",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://library.iitd.ac.in/etd",
        "notes":            "Institutional license; no AI policy",
    },
    {
        "institution":      "IIT Bombay",
        "license_type":     "Institutional",
        "license_detail":   "IIT Bombay institutional repository deposit agreement",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://library.iitb.ac.in/etd",
        "notes":            "Institutional license; no AI policy",
    },
    {
        "institution":      "IIT Madras",
        "license_type":     "Institutional",
        "license_detail":   "IIT Madras ETD deposit agreement",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://library.iitm.ac.in",
        "notes":            "Institutional license; no AI policy",
    },
    {
        "institution":      "MIT DSpace",
        "license_type":     "CC-BY",
        "license_detail":   "CC-BY 4.0 default; author may choose CC-BY-NC",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://libraries.mit.edu/scholarly/publishing/dspace-mit/",
        "notes":            "CC-BY does not address AI training",
    },
    {
        "institution":      "Virginia Tech VTechWorks",
        "license_type":     "CC-BY",
        "license_detail":   "CC-BY 4.0 — VTechWorks ETD submission policy",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://vtechworks.lib.vt.edu/",
        "notes":            "CC-BY; no AI policy",
    },
    {
        "institution":      "UCLA eScholarship",
        "license_type":     "Mixed",
        "license_detail":   "Varies by author choice: CC-BY, CC-BY-NC, or All Rights Reserved",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://escholarship.org/submit",
        "notes":            "Mixed licenses; no uniform AI policy",
    },
    {
        "institution":      "Univ. of Michigan Deep Blue",
        "license_type":     "CC-BY",
        "license_detail":   "CC-BY 4.0 — Deep Blue Repositories deposit agreement",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://deepblue.lib.umich.edu/",
        "notes":            "CC-BY; no AI policy",
    },
    {
        "institution":      "Australian National Univ.",
        "license_type":     "CC-BY",
        "license_detail":   "CC-BY 4.0 — ANU Open Research repository policy",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://openresearch-repository.anu.edu.au/",
        "notes":            "CC-BY; no AI policy",
    },
    {
        "institution":      "EThOS",
        "license_type":     "Subscription",
        "license_detail":   "British Library EThOS — restricted; some OA theses CC-BY",
        "ai_use_explicit":  False,
        "ai_permitted":     False,   # scraping likely unauthorised
        "gap":              True,
        "source_url":       "https://ethos.bl.uk/",
        "notes":            "Restricted access; CC crawling likely unauthorised yet occurring",
    },
    {
        "institution":      "DART Europe",
        "license_type":     "CC-BY",
        "license_detail":   "CC-BY — DART Europe portal aggregates OA European ETDs",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://dart-europe.org/",
        "notes":            "CC-BY; no AI policy",
    },
    {
        "institution":      "NDLTD Union Catalog",
        "license_type":     "Mixed",
        "license_detail":   "Aggregator — license varies by member institution",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://union.ndltd.org/",
        "notes":            "Mixed; no uniform AI policy",
    },
    {
        "institution":      "OATD",
        "license_type":     "Mixed",
        "license_detail":   "Aggregator — links to OA theses; license varies",
        "ai_use_explicit":  False,
        "ai_permitted":     None,
        "gap":              True,
        "source_url":       "https://oatd.org/",
        "notes":            "Mixed; no uniform AI policy",
    },
    {
        "institution":      "ProQuest Dissertations",
        "license_type":     "Subscription",
        "license_detail":   "ProQuest PQDT — commercial subscription; all rights reserved",
        "ai_use_explicit":  False,
        "ai_permitted":     False,
        "gap":              True,
        "source_url":       "https://proquest.com/pqdtglobal",
        "notes":            "Subscription/restricted; AI training use clearly unauthorised",
    },
]


def classify_gap(row: dict) -> str:
    """Return a human-readable gap classification."""
    if row["license_type"] == "CC-BY":
        return "CC-BY — gap (AI use unaddressed)"
    elif row["license_type"] == "CC-BY-NC":
        return "CC-BY-NC — partial protection (commercial AI training arguably prohibited)"
    elif row["license_type"] == "Institutional":
        return "Institutional — gap (no AI clause)"
    elif row["license_type"] == "Mixed":
        return "Mixed — gap (varies by document)"
    elif row["license_type"] == "Subscription":
        return "Subscription — gap (no explicit AI prohibition; yet crawled)"
    return "Unknown"


def run_license_audit() -> pd.DataFrame:
    os.makedirs("results", exist_ok=True)

    df = pd.DataFrame(LICENSE_DATA)
    df["gap_classification"] = df.apply(classify_gap, axis=1)

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✓ License audit complete → {OUTPUT_CSV}")

    # Summary stats
    n_total    = len(df)
    n_gap      = df["gap"].sum()
    n_cc_by    = (df["license_type"] == "CC-BY").sum()
    n_inst     = (df["license_type"] == "Institutional").sum()
    n_mixed    = (df["license_type"] == "Mixed").sum()
    n_sub      = (df["license_type"] == "Subscription").sum()

    print(f"\nLicensing gap analysis:")
    print(f"  Total institutions : {n_total}")
    print(f"  With gap           : {n_gap} ({100*n_gap/n_total:.1f}%)")
    print(f"  CC-BY              : {n_cc_by} ({100*n_cc_by/n_total:.1f}%)")
    print(f"  Institutional      : {n_inst} ({100*n_inst/n_total:.1f}%)")
    print(f"  Mixed              : {n_mixed} ({100*n_mixed/n_total:.1f}%)")
    print(f"  Subscription       : {n_sub} ({100*n_sub/n_total:.1f}%)")

    return df


if __name__ == "__main__":
    run_license_audit()
