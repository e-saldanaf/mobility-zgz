# 🚲 Mobility Zaragoza — Bizi Data Platform

A two-component data platform built around the public bike-sharing network of Zaragoza (Bizi), using the city's Open Data API.

---

## Architecture

```
Zaragoza Open Data API
        │
        ├──────────────────────────────────┐
        │                                  │
        ▼                                  ▼
 [ ETL Pipeline ]                 [ Streamlit Dashboard ]
 Python · SQLAlchemy               Real-time API call
 Upsert → PostgreSQL               No DB dependency
 Scheduled manually                Always fresh data
```

The platform has two independent components with intentionally separate data flows:

- **ETL Pipeline** — extracts, transforms and loads station snapshots into PostgreSQL for historical analysis. Designed for scheduled execution (cron, Airflow).
- **Streamlit Dashboard** — calls the Open Data API directly on each user request, bypassing the database entirely. This is a deliberate architectural decision: the free tier of GitHub Actions does not support frequent scheduled runs, so a live API call guarantees real-time data without depending on pipeline execution frequency.

---

## Components

### 1. ETL Pipeline (`src/`)

A Python ETL pipeline that ingests station data from the Zaragoza Open Data REST API, normalizes it with Pandas, and loads it into PostgreSQL using an idempotent upsert strategy.

| Phase | Module | Responsibility |
|---|---|---|
| Extract | `src/extract.py` | Fetches JSON snapshot from the API |
| Transform | `src/transform.py` | Normalizes fields, casts types, adds audit columns |
| Load | `src/load.py` | Upserts into PostgreSQL via temp table + `ON CONFLICT` |

**Run manually:**
```bash
python main.py
```

**Key engineering decisions:**
- **Upsert over insert** — idempotent by design, safe to run repeatedly
- **Modular structure** — each phase is independently testable
- **Audit columns** — `created_at`, `modified_at`, `action` added at transform time

---

### 2. Live Dashboard (`dashboard/`)

A Streamlit application that displays real-time Bizi station availability on an interactive map, with dual visualization modes and station-level detail.

**Live app:** [bizi-zgz.streamlit.app](https://bizi-zgz.streamlit.app/)

**Features:**
- 🚲 / 🅿️ toggle — switch between "find a bike" and "find a dock" visualization modes
- Color gradient — green → yellow → orange → red based on availability ratio
- KPI metrics — total bikes, docks, active stations, critical stations
- Sidebar filters — minimum availability, hide empty stations
- Interactive map — Pydeck ScatterplotLayer with tooltip on hover
- Station table — sorted by station number, with progress bar showing occupancy

**Run locally:**
```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

**Why direct API calls instead of the database?**
The GitHub Actions free tier limits scheduled workflow execution frequency, which would result in stale data in the database. Calling the Open Data API directly on each Streamlit request guarantees real-time accuracy without infrastructure cost. If a production-grade scheduled pipeline were available (e.g. Airflow on a dedicated server), the dashboard could be refactored to query the historical database and add time-series analysis.

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Transformation | Pandas |
| DB Connectivity | SQLAlchemy / Psycopg |
| Data Store | Supabase (PostgreSQL) |
| Dashboard | Streamlit + Pydeck |
| HTTP Client | Requests |
| Config | python-dotenv |

---

## Setup

### ETL Pipeline

```bash
# Clone
git clone https://github.com/e-saldanaf/mobility-zgz.git
cd mobility-zgz

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run
python main.py
```

### Dashboard

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

---

## Data Source

[Open Data Portal — Ayuntamiento de Zaragoza](https://www.zaragoza.es/sede/portal/datos-abiertos/)

---

## License

Released under the [Unlicense](LICENSE) — public domain, no restrictions.