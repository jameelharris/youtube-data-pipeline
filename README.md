# youtube-data-pipeline

An end-to-end data pipeline that ingests YouTube channel and video data from the
YouTube Data API v3 and transforms it into curated, analytics-ready tables using a
medallion architecture (bronze → silver → gold) on Databricks.

## Stack
- **Ingestion:** YouTube Data API v3 (REST)
- **Processing:** Databricks, PySpark, Spark SQL
- **Storage:** Delta Lake
- **Architecture:** Medallion (bronze / silver / gold)

## Status
Work in progress.

## Notes
- API access uses a key read from the `YT_API_KEY` environment variable; no
  credentials are committed to the repository.
