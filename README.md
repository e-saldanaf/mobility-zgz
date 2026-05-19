# 🚲 Mobility Zaragoza — Bizi ETL Pipeline

A Python ETL pipeline that ingests real-time data from the **Open Data API of Zaragoza City Council**, processes public bike-sharing station statuses (Bizi), and loads them into a PostgreSQL database using an idempotent upsert strategy.

---

## 📐 Architecture

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│       EXTRACT        │────▶│      TRANSFORM        │────▶│        LOAD          │
│                     │     │                      │     │                     │
│  Zaragoza Open Data │     │  Normalize & clean   │     │  Upsert into        │
│  REST API (JSON)    │     │  stations payload    │     │  PostgreSQL         │
│  src/extract.py     │     │  src/transform.py    │     │  src/load.py        │
└─────────────────────┘     └──────────────────────┘     └─────────────────────┘
```

Each ETL phase is isolated in its own module, making the pipeline independently testable and maintainable.

---

## 🛠️ Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Transformation | Pandas |
| DB Connectivity | SQLAlchemy / Psycopg |
| Data Store | Supabase (PostgreSQL) |
| HTTP Client | Requests |
| Config | python-dotenv |

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/e-saldanaf/mobility-zgz.git
cd mobility-zgz
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL="postgresql://user:password@host:port/database"
```

> ⚠️ Never commit your `.env` file. It is already listed in `.gitignore`.

### 5. Run the pipeline

```bash
python main.py
```

The console will log how many stations were processed and confirm the upsert into the database.

---

## 📁 Project Structure

```
mobility-zgz/
│
├── src/
│   ├── extract.py       # Connects to Zaragoza Open Data API
│   ├── transform.py     # Cleans and normalizes the stations payload
│   └── load.py          # Upserts data into PostgreSQL
│
├── query/
│   └── postgresql/
│       └── create/
│           └── bizi_stations/   # DDL scripts for table creation
│
├── main.py              # Pipeline entrypoint
├── requirements.txt
├── pyproject.toml
└── .env.example
```

---

## 🔑 Key Engineering Decisions

**Upsert over insert**
Guarantees idempotency — safe to run on a schedule (e.g. via cron or Airflow) without duplicating records.

**Modular ETL structure**
Each phase (Extract, Transform, Load) lives in its own module. You can test, mock or replace any phase independently without touching the others.

**Environment-based configuration**
Database credentials are loaded from environment variables via `python-dotenv`. No secrets are hardcoded or committed to version control.

---

## 📡 Data Source

Data is extracted in real time from the open infrastructure services of the **Ayuntamiento de Zaragoza**:

[Open Data Portal — Zaragoza City Council](https://www.zaragoza.es/sede/portal/datos-abiertos/)

---

## 📄 License

This project is released under the [Unlicense](LICENSE) — public domain, no restrictions.
