# ETD Audit: Harvested Without Consent

Replication code and data for:

> **"Harvested Without Consent: ETDs as LLM Fine-Tuning Data — An Empirical Audit and Institutional Governance Framework"**  
> Aakansha Jagga, Guru Gobind Singh Indraprastha University, New Delhi, India  
> Submitted to JCDL 2026 Undergraduate Research Symposium

---

## Repository Structure

```
etd-audit/
├── scripts/
│   ├── cc_audit.py          # Phase 1: Common Crawl domain audit
│   ├── manifest_audit.py    # Phase 2: Dataset manifest analysis
│   ├── license_audit.py     # Phase 3: Licensing gap analysis
│   ├── robots_audit.py      # Validation: robots.txt CCBot check
│   └── generate_figures.py  # Reproduce all paper figures
├── data/
│   ├── raw/                 # Raw JSON from CC Index API queries
│   ├── processed/           # Cleaned CSVs used in analysis
│   └── institutions.csv     # Master institution list with metadata
├── results/
│   ├── exposure_scores.csv  # Final exposure scores (Table 1)
│   ├── license_gap.csv      # Licensing analysis (Figure 2)
│   └── robots_audit.csv     # robots.txt validation results
├── docs/
│   └── methodology.md       # Extended methodology notes
└── requirements.txt
```

## Quickstart

```bash
pip install -r requirements.txt

# Run full audit pipeline
python scripts/cc_audit.py
python scripts/manifest_audit.py
python scripts/license_audit.py
python scripts/robots_audit.py

# Reproduce figures
python scripts/generate_figures.py
```

## Institutions Audited

15 NDLTD-affiliated ETD repositories spanning Global North, Global South, Global aggregators, and Commercial:

| Institution | Domain | Region |
|---|---|---|
| IISc Bangalore | etd.iisc.ac.in | Global South |
| Shodhganga | shodhganga.inflibnet.ac.in | Global South |
| IIT Delhi | etd.iitd.ac.in | Global South |
| IIT Bombay | etd.iitb.ac.in | Global South |
| IIT Madras | etd.iitm.ac.in | Global South |
| MIT DSpace | dspace.mit.edu | Global North |
| Virginia Tech | vtechworks.lib.vt.edu | Global North |
| UCLA eScholarship | escholarship.org | Global North |
| Univ. of Michigan | deepblue.lib.umich.edu | Global North |
| Australian National Univ. | openresearch-repository.anu.edu.au | Global North |
| EThOS | ethos.bl.uk | Global North |
| DART Europe | dart-europe.org | Global North |
| NDLTD Union Catalog | union.ndltd.org | Global |
| OATD | oatd.org | Global |
| ProQuest Dissertations | proquest.com/pqdtglobal | Commercial |

## Common Crawl Indexes Queried

- CC-MAIN-2022-21
- CC-MAIN-2022-49
- CC-MAIN-2023-14
- CC-MAIN-2023-40
- CC-MAIN-2024-10

## Reproducibility

All raw API responses are stored in `data/raw/` as JSON files named `{domain}_{index}.json`.  
All figures in the paper can be reproduced by running `python scripts/generate_figures.py`.

## License

Code: MIT License  
Data: CC-BY 4.0

## Citation

```bibtex
@inproceedings{jagga2026harvested,
  title     = {Harvested Without Consent: ETDs as LLM Fine-Tuning Data},
  author    = {Jagga, Aakansha},
  booktitle = {Proceedings of the JCDL 2026 Undergraduate Research Symposium},
  year      = {2026}
}
```
