# Reproducible local PostgreSQL demo (synthetic incidents only)

This optional development environment uses Docker Compose and the checked-in
**simulated** `data/network_incidents.csv`. It does not connect to any
telecom production system or paid cloud service. PostgreSQL listens on
**127.0.0.1:5433 only**, not on a public network interface.

## Prerequisites

- Docker Engine/Desktop with the `docker compose` plugin
- Python 3 for offline standard-library tests
- Run all commands from the repository root.

## Start the local database

Set a temporary password in the current shell (do not commit it or put it
in the repository). This generates a random value; keep the same shell
session for all commands below:

```sh
export POSTGRES_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
docker compose up -d db
docker compose ps
```

The first start downloads the public `postgres:16-alpine` image if needed.
Wait for the `db` health check to report healthy before importing.

## Create schema and import CSV once

```sh
docker compose exec -T db psql -U incident_demo -d incident_demo -v ON_ERROR_STOP=1 -f /workspace/sql/01_incident_schema.sql
docker compose exec -T db psql -U incident_demo -d incident_demo -v ON_ERROR_STOP=1 -c "\copy incident_events FROM '/workspace/data/network_incidents.csv' WITH (FORMAT csv, HEADER true)"
docker compose exec -T db psql -U incident_demo -d incident_demo -v ON_ERROR_STOP=1 -c "SELECT COUNT(*) AS incident_count FROM incident_events;"
```

The expected count for the current checked-in fixture is **150**.
The `incident_id` primary key rejects duplicate imports; the CSV import
is **not idempotent**. Do not rerun it against a populated table. Source
timestamps have no timezone and are stored as `timestamp without time zone`;
no UTC assumption is made.

## Run read-only reports and offline parity checks

```sh
docker compose exec -T db psql -U incident_demo -d incident_demo -v ON_ERROR_STOP=1 -f /workspace/sql/02_reporting_queries.sql
python3 -m unittest discover -s tests -v
```

The SQL file returns category, severity, and category-by-severity counts
and average resolution times. The Python parity tests compare the three
SELECT queries to published summary CSVs **using SQLite in memory**. They
do not execute PostgreSQL, so both the Docker commands and the offline
tests are needed to validate different parts of the project.

To stop the local service without deleting its persistent database volume:

```sh
docker compose down
```

The `incident_pgdata` Docker volume persists. Subsequent starts retain
the imported rows; do not repeat the import. To create a clean environment,
use a fresh Docker Compose project name/volume after separately reviewing
any data that would be discarded.

## Scope and limitations

- Only synthetic data is permitted. Never replace it with customer or
  production network logs.
- No real-time pipeline, dashboard, cloud deployment, or production
  PostgreSQL integration is implied.
- The Docker image tag is not digest-pinned; for stricter reproducibility,
  pin a reviewed image digest in a later change.
- The SQL summaries are descriptive; they do not establish causality or
  prediction performance.
