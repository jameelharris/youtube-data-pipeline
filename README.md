# Citibike Trip Analysis on Databricks (PySpark · Delta Lake · Spark SQL)

An end-to-end Databricks notebook that ingests real NYC Citibike trip data, transforms it with PySpark, persists the result as a Delta Lake table, and demonstrates the Delta features that distinguish a Lakehouse table from plain Parquet — plus Spark SQL querying. Built and run on Databricks Free Edition (serverless compute, Unity Catalog).

## What this demonstrates

- **PySpark** — reading a multi-file CSV dataset (~2.3M rows) into a DataFrame, filtering, grouping, and aggregating with the DataFrame API.
- **Delta Lake** — writing a managed Delta table, then exercising `MERGE` (upsert), time travel (`VERSION AS OF`), and `OPTIMIZE ... ZORDER`.
- **Spark SQL** — querying the Delta table and the raw data via both the `%sql` magic and `spark.sql()`.
- **Databricks** — Unity Catalog volumes for staging, managed tables, serverless notebook execution.

## The dataset

NYC Citibike public trip data, December 2024 (~2.31M rows), published by Citi Bike at https://citibikenyc.com/system-data. The data is pre-cleaned by the publisher: staff/service trips, test-station trips, and sub-60-second trips are already removed. December tops one million trips, so the month ships as three split CSVs, which the notebook reads together with a wildcard path.

## The pipeline

1. **Ingest** — download the monthly zip, extract the CSVs, and copy them into a Unity Catalog volume so the cluster can read them.
2. **Read & explore** — load all CSV splits into one DataFrame, inspect schema and row count.
3. **Transform** — compute the ten busiest start stations (filter null station IDs, group by station, count, order, limit).
4. **Write to Delta** — save the result as a managed Delta table via `saveAsTable`.
5. **Delta features** — `MERGE` an update batch (one update, one insert), query a prior version with time travel, and run `OPTIMIZE ZORDER`.
6. **Spark SQL** — re-express queries in SQL, including a member-vs-casual rider breakdown.

## Results (top 10 stations, Dec 2024)

| start_station_id | start_station_name      | count |
|------------------|-------------------------|-------|
| 6140.05          | W 21 St & 6 Ave         | 8946  |
| 6331.01          | W 31 St & 7 Ave         | 8039  |
| 5905.12          | Broadway & E 14 St      | 7672  |
| 5788.13          | Lafayette St & E 8 St   | 7582  |
| 5905.14          | University Pl & E 14 St  | 7558  |

All midtown/downtown Manhattan, as expected. Members accounted for ~87% of December rides (2.02M vs 292K casual) — the winter skew toward commuters over tourists.

## Notes on a few deliberate choices

- **No `.cache()` on the aggregation.** The top-ten result is materialized exactly once, so caching would add memory pressure with no benefit. Caching pays off when a DataFrame is reused across multiple actions; this isn't the case.
- **`OPTIMIZE` on a 10-row table is illustrative, not impactful.** Compaction and Z-ordering matter for large tables that accumulate many small files from frequent writes. The notebook runs it to show the operation and explain *when* it matters, not to claim a speedup on a toy table.
- **`inferSchema` for convenience.** A production job would define an explicit schema to avoid the extra data scan and to lock column types; inference is fine for an exploratory demo.

## Running it yourself

1. Sign up for [Databricks Free Edition](https://www.databricks.com/learn/free-edition).
2. Create a Python notebook (serverless compute attaches automatically).
3. Run the notebook cells top to bottom. The default Unity Catalog location is `workspace.default`; adjust the catalog/schema names if your workspace differs.

## Files

- `citibike_delta_demo.ipynb` — the full notebook with outputs.
