# 🚲 Mobility Zaragoza — Bizi ETL Pipeline

A Python ETL pipeline that ingests real-time data from the **Open Data API of Zaragoza City Council**, processes public bike-sharing station statuses (Bizi), and loads them into a PostgreSQL database.

---

## 📐 Architecture

```
┌─────────────────────┐     ┌──────────────────────┐     ┌──────────────┐
│       EXTRACT        │────▶│      TRANSFORM        │────▶│        LOAD          │
│                     │     │                      │     │                     │
│  Zaragoza Open Data │     │  Normalize & clean   │     │  Upsert into        │
│  REST API (JSON)    │     │  stations payload    │     │  PostgreSQL         │
│  src/extract.py     │     │  src/transform.py    │     │  src/load.py        │
└─────────────────────┘     └──────────────────────┘     └──────────────┘
```

Each ETL phase is isolated in its own module, making the pipeline independently testable and maintainable.

---

## 🛠️ Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Transformation | Pandas |
| DB Connectivity | SQLAlchemy / psycopg |
| Data Store | Supabase (PostgreSQL) |
| HTTP Client | requests |
| Config | python-dotenv |

---

## ⚙️ Setup

### Requisitos

- Python 3.10+ (recomendado). Si usas pyenv: `pyenv install 3.10.12`.
- pip, virtualenv o venv.

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

Se ha añadido un archivo de ejemplo `.env.example` en la rama `docs/add-contributing-and-env`. Copialo a `.env` y rellena las credenciales necesarias.

```env
DATABASE_URL="postgresql://user:password@host:port/database"
BIZI_API_URL="https://www.zaragoza.es/some/endpoint?rf=json"
# SUPABASE_URL and SUPABASE_KEY si procede
```

> ⚠️ Nunca commits tu `.env`. Está incluido en `.gitignore`.

### 5. Ejecutar pipeline

```bash
python main.py
```

La consola mostrará cuántas estaciones se procesaron y confirmará el upsert en la base de datos.

---

## ✅ Ejecutar tests

Si añades o modificas lógica, por favor incluye tests. Para ejecutar los tests:

```bash
pytest
```

(Si no hay tests en la rama actual, se agradecen aportes en `tests/`).

---

## 📁 Project Structure

```
mobility-zgz/
│
├── src/
│   ├── extract.py       # Conecta con Zaragoza Open Data API
│   ├── transform.py     # Limpia y normaliza el payload de estaciones
│   └── load.py          # Upserts en PostgreSQL
│
├── query/
│   └── postgresql/      # DDL scripts para creación de tablas (nota: confirmar nombre de carpeta)
│
├── main.py              # Entrypoint del pipeline
├── requirements.txt
├── pyproject.toml
├── .env.example         # Ejemplo de variables de entorno (añadido)
└── README.md
```

---

## 🔑 Key Engineering Decisions

**Upsert sobre insert** — Garantiza idempotencia: seguro para ejecutar periódicamente sin duplicar registros.

**Modular ETL** — Cada fase (Extract, Transform, Load) vive en su módulo propio. Permite pruebas unitarias y mocks.

**Configuración por entorno** — Credenciales cargadas desde variables de entorno con `python-dotenv`.

---

## 📡 Data Source

Datos extraídos en tiempo real de los servicios de datos abiertos del **Ayuntamiento de Zaragoza**:

[Open Data Portal — Zaragoza City Council](https://www.zaragoza.es/sede/portal/datos-abiertos/)

---

## 📄 License

This project is released under the [Unlicense](LICENSE) — public domain, no restrictions.

---

## Contributing

Si vas a contribuir, revisa `CONTRIBUTING.md` en la raíz del repositorio para las pautas.
