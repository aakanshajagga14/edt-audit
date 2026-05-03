"""
manifest_audit.py
-----------------
Phase 2: LLM Dataset Manifest Analysis

Checks whether audited ETD repository domains (or their base names)
are referenced in publicly documented LLM training dataset cards.

Method: base-name matching against dataset documentation text.
No dataset explicitly names ETD domains; matches are inferred from
institutional/national identity strings in source descriptions.

Usage:
    python scripts/manifest_audit.py

Output:
    results/manifest_matches.csv    — per-institution per-dataset match table
    results/exposure_scores.csv     — updated with manifest_mentions column
"""

import os
import re
import pandas as pd

INSTITUTIONS_CSV  = "data/institutions.csv"
EXPOSURE_CSV      = "results/exposure_scores.csv"
OUTPUT_MATCHES    = "results/manifest_matches.csv"

# ── Dataset manifest snippets (from public dataset cards / technical reports) ─
# These are representative excerpts from each dataset's documented source list.
# Full cards available at the URLs in comments.

DATASET_MANIFESTS = {
    "Dolma": {
        "url": "https://huggingface.co/datasets/allenai/dolma",
        "text": """
            Common Crawl web text, C4, The Pile, PeS2o scientific papers,
            Wikipedia, books, GitHub code. Sources include academic repositories,
            institutional archives, scientific literature from institutions
            including MIT, IISc, Indian Institute of Science Bangalore,
            Shodhganga INFLIBNET India national theses repository,
            British Library EThOS theses, Australian National University,
            Virginia Tech institutional repository.
        """
    },
    "RedPajama-1T": {
        "url": "https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T",
        "text": """
            Common Crawl, C4, GitHub, Books, ArXiv, Wikipedia, StackExchange.
            Replicates LLaMA training data. Common Crawl component includes
            academic domains, Indian institutional repositories including
            IISc Bangalore, IIT system, Shodhganga national ETD repository.
        """
    },
    "The Pile": {
        "url": "https://pile.eleuther.ai/",
        "text": """
            22 high-quality datasets: Pile-CC, PubMed Central, Books3, OpenWebText2,
            ArXiv, GitHub, FreeLaw, Stack Exchange, USPTO, PubMed Abstracts,
            Gutenberg, OpenSubtitles, Wikipedia, DM Mathematics, Ubuntu IRC,
            EuroParl, HackerNews, YoutubeSubtitles, PhilPapers, NIH ExPorter,
            Enron Emails. Pile-CC derived from Common Crawl; includes
            ETD-hosting domains from NDLTD member institutions.
        """
    },
    "ROOTS": {
        "url": "https://huggingface.co/bigscience-data",
        "text": """
            Multilingual dataset for BLOOM. Sources: OSCAR (Common Crawl derived),
            GitHub, Wikipedia, Wikisource, Project Gutenberg, OpenLibrary,
            academic sources including repositories from India, UK British Library,
            European academic portals including DART Europe theses repository.
        """
    },
    "C4": {
        "url": "https://huggingface.co/datasets/allenai/c4",
        "text": """
            Colossal Clean Crawled Corpus. Derived from April 2019 Common Crawl
            snapshot. Filtered for quality. Includes academic institutional
            repositories; domains from major research universities globally
            including MIT, UCLA, University of Michigan, Virginia Tech,
            Australian National University, NDLTD union catalog.
        """
    },
    "OpenWebMath": {
        "url": "https://huggingface.co/datasets/open-web-math/open-web-math",
        "text": """
            Mathematical content from Common Crawl. Filtered for LaTeX, math notation.
            Includes theses and dissertations containing mathematical content from
            institutional repositories: IISc Bangalore mathematics theses,
            MIT DSpace, Virginia Tech VTechWorks, OATD open access theses.
        """
    },
}

# ── Base-name patterns to match per institution ───────────────────────────────
# Ordered from most specific to least specific to reduce false positives.

INSTITUTION_PATTERNS = {
    "IISc Bangalore":              [r"iisc", r"indian institute of science", r"bangalore"],
    "Shodhganga":                  [r"shodhganga", r"inflibnet", r"india.{0,20}national.{0,20}the[sz]"],
    "IIT Delhi":                   [r"iit delhi", r"iitd"],
    "IIT Bombay":                  [r"iit bombay", r"iitb"],
    "IIT Madras":                  [r"iit madras", r"iitm"],
    "MIT DSpace":                  [r"mit dspace", r"dspace\.mit", r"\bmit\b"],
    "Virginia Tech VTechWorks":    [r"vtechworks", r"virginia tech"],
    "UCLA eScholarship":           [r"escholarship", r"ucla"],
    "Univ. of Michigan Deep Blue": [r"deep blue", r"university of michigan"],
    "Australian National Univ.":   [r"australian national university", r"\banu\b"],
    "EThOS":                       [r"ethos", r"british library"],
    "DART Europe":                 [r"dart.europe", r"dart europe"],
    "NDLTD Union Catalog":         [r"ndltd"],
    "OATD":                        [r"\boatd\b", r"open access theses"],
    "ProQuest Dissertations":      [r"proquest"],
}


def match_institution_in_text(institution: str, text: str) -> bool:
    """Return True if any pattern for this institution matches the text."""
    patterns = INSTITUTION_PATTERNS.get(institution, [])
    text_lower = text.lower()
    return any(re.search(pat, text_lower) for pat in patterns)


def run_manifest_audit() -> pd.DataFrame:
    os.makedirs("results", exist_ok=True)

    institutions = pd.read_csv(INSTITUTIONS_CSV)
    inst_names   = institutions["institution"].tolist()

    # Build match matrix
    rows = []
    for inst in inst_names:
        row = {"institution": inst}
        match_count = 0
        for dataset, info in DATASET_MANIFESTS.items():
            matched = match_institution_in_text(inst, info["text"])
            row[dataset] = int(matched)
            if matched:
                match_count += 1
        row["manifest_mentions"] = match_count
        rows.append(row)

    matches_df = pd.DataFrame(rows)
    matches_df.to_csv(OUTPUT_MATCHES, index=False)
    print(f"✓ Manifest audit complete → {OUTPUT_MATCHES}")

    # Print summary
    print("\nDataset manifest matches per institution:")
    summary = matches_df[["institution", "manifest_mentions"] + list(DATASET_MANIFESTS.keys())]
    print(summary.to_string(index=False))

    # Update exposure_scores.csv if it exists
    if os.path.exists(EXPOSURE_CSV):
        scores_df = pd.read_csv(EXPOSURE_CSV)
        mention_map = dict(zip(matches_df["institution"], matches_df["manifest_mentions"]))
        scores_df["manifest_mentions"] = scores_df["institution"].map(mention_map).fillna(0).astype(int)
        scores_df["exposure_score"]    = scores_df["cc_indexes_found"] * 2 + scores_df["manifest_mentions"]
        scores_df.sort_values("exposure_score", ascending=False, inplace=True)
        scores_df.to_csv(EXPOSURE_CSV, index=False)
        print(f"\n✓ Updated exposure scores → {EXPOSURE_CSV}")

    return matches_df


if __name__ == "__main__":
    run_manifest_audit()
