# Extended Methodology Notes

## Common Crawl Index API

The CC Index API is a public REST endpoint maintained by Common Crawl:
https://index.commoncrawl.org/

Exact query pattern used in this audit:
```
GET https://index.commoncrawl.org/{INDEX}-index?url={domain}/*&output=json&limit=10
```

**Interpretation caveat:** CC index presence = the domain was crawled and archived.
It does NOT confirm the content was ingested into any specific model's training run.
The inference chain involves uncertainty at each step. All claims in the paper use
the language "likely exposed to LLM training pipelines" to reflect this.

## Exposure Score Formula

    Exposure Score = (CC Indexes Found × 2) + Dataset Manifest Mentions

The x2 weight on CC indexes reflects that Common Crawl is the direct upstream
source for all six corpora examined. Manifest mentions are lower-bound estimates
(no manifest explicitly names any ETD domain). A sensitivity analysis with factor=1
does not materially change the rank ordering.

## robots.txt Validation

All 15 domains were checked for CCBot exclusion rules in January 2026.
IIT Delhi explicitly blocks all crawlers (User-agent: * / Disallow: /).
No other institution blocked CCBot.
This confirms the governance vacuum is a policy failure, not a technical one.

## Licensing Gap Operationalisation

A licensing gap is coded as TRUE when the stated license:
- Neither explicitly permits AI training use
- Nor explicitly prohibits AI training use

CC-BY and CC-BY-NC are both coded as gap=TRUE since the CC license suite
predates LLMs and does not address computational ingestion at scale.
