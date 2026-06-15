# Triton Poker: YouTube Content Strategy Analysis

An end-to-end data pipeline on **Databricks** that ingests, classifies, and analyzes the
~950-video YouTube catalog of the **Triton Poker Series**. The full analysis, findings, and
content-strategy recommendation live in the notebook; this README covers the engineering.

**Notebook:** [`Triton Poker Channel Analytics.ipynb`](./Triton%20Poker%20Channel%20Analytics.ipynb) *(analysis & findings)*

---

## Architecture

A **medallion (bronze → silver → gold)** pipeline, all under the Unity Catalog namespace
`workspace.youtube`:

```
YouTube Data API v3  ──►  bronze_videos_raw  ──►  silver_videos  ──►  gold_* (5 tables)
   (REST, ingest)          (raw JSON, Delta)      (typed + classified)   (curated aggregations)
                                                         ▲
                                                    ref_stops
                                                 (reference lookup)
```

| Layer | Table(s) | Role |
|---|---|---|
| **Bronze** | `bronze_videos_raw` | Raw, immutable API responses — one row per video, full JSON in `raw_json`, plus provenance (`video_id`, `ingested_at`). No parsing. |
| **Reference** | `ref_stops` | Externalized lookup (canonical stop name + alias regex), joined by silver. Reference data as data, not hardcoded logic. |
| **Silver** | `silver_videos` | Typed/cleaned/classified — one row per video with four orthogonal dimensions (`is_live_broadcast`, `duration_bucket`, `stop_location`, `game_format`) and data-quality flags. |
| **Gold** | `gold_engagement_by_duration`, `gold_engagement_by_game_format`, `gold_engagement_by_stop`, `gold_engagement_cross`, `gold_top_videos_by_engagement` | Curated, analytics-ready aggregations. |

### Ingestion

Raw data is extracted from the **YouTube Data API v3** (REST) and landed in the bronze Delta
table. Extraction logic is also packaged as a standalone, reusable script
([`ingest_youtube.py`](./ingest_youtube.py)).

- **Cost-optimized path:** resolves the channel's uploads playlist and pages it
  (`playlistItems`, 1 quota unit/page) plus batch `videos` lookups (1 unit / 50 IDs), rather than
  the `search` endpoint (100 units/call). A full ~950-video run costs ~40 of the 10,000 daily
  quota units.
- **Credentials:** the API key is read from a **Databricks secret scope**
  (`scope="youtube"`, `key="api_key"`), never hardcoded or committed.

### Transforms

- **Silver** parses `raw_json` via Spark SQL colon syntax with `try_cast` (malformed values → null
  rather than job failure), derives `duration_seconds` from ISO-8601, joins `ref_stops` for
  location (title-first, deterministic best-match via `ROW_NUMBER`), and derives duration/game-format
  buckets.
- All tables use `CREATE OR REPLACE` for **idempotent**, reproducible rebuilds.
- Engagement metric (gold): `(likes + comments) / views`, computed as ratio-of-sums per group.

---

## Tech stack

| | |
|---|---|
| Platform | Databricks (Free Edition) — Unity Catalog, secret scopes |
| Storage | Delta Lake |
| Transforms | Spark SQL |
| Ingestion | PySpark + Python (`requests`, `python-dotenv`) |
| Source | YouTube Data API v3 (REST) |

---

## Skills demonstrated

| Competency | Where |
|---|---|
| Medallion architecture | Bronze/silver/gold layering |
| Delta Lake | All tables; idempotent `CREATE OR REPLACE` |
| Spark SQL | Silver transform + gold aggregations |
| PySpark | Ingestion, JSON-to-Delta landing |
| REST API integration | YouTube Data API v3 (`ingest_youtube.py`) |
| Dimensional modeling | Four orthogonal silver dimensions; `ref_stops` reference dimension |
| Reference data over hardcoded logic | `ref_stops` lookup |
| Data quality & validation | Tag-reliability check, duration validation, game-format coverage, tag-taxonomy finding |
| Unity Catalog / cataloging | Dedicated `youtube` schema across layers |
| Cost optimization | Uploads-playlist ingestion vs. `search` endpoint |
| Analytical rigor | Confound identification & control (duration confound) |
| Git / version control | This repository |

---

## Repository layout

```
.
├── Triton Poker Channel Analytics.ipynb   # the pipeline + analysis (start here)
├── ingest_youtube.py               # standalone REST extraction script
├── README.md
└── .gitignore
```

---

## Limitations & production considerations

**Limitations of the current build:**
- Engagement rate is a **public-data proxy** (`(likes+comments)/views`); YouTube's core signals
  (watch time, retention, CTR) are owner-only and inaccessible via the public API.
- **Single snapshot** — one batch pull, so trends are inferred from a static catalog; cross-video
  comparisons use engagement *rate* rather than age-biased raw views.
- Classification is reliable for length/broadcast type, **best-effort** for game format
  (~34% undeterminable) and location (~90% matched).

**What a production version would add:**
- **Scheduled, incremental ingestion** — Databricks Job + Delta `MERGE` upserts instead of full
  `CREATE OR REPLACE`.
- **Time-series snapshots** — periodic captures with Delta time travel, enabling velocity analysis
  a single snapshot can't support.
- **CI/CD** — automated testing and deployment.
- **BI serving** — gold tables structured for Power BI / Tableau / Looker.
- **Content taxonomy** — the public tag layer is incoherent (see notebook's data-quality section);
  a real taxonomy would enable systematic content-type performance measurement.