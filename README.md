# Containerized Apps

A Docker Compose demo with two Flask services behind an Nginx reverse proxy and a shared PostgreSQL database. This project demonstrates container networking, service separation, persistent storage, and basic database operations.

## Features

- **Service B:** Add people by first and last name, check for existing records, and display the total record count.
- **Service C:** List saved records, delete individual records, and display the remaining count.
- **Nginx:** Route requests to each application through a separate host port.
- **PostgreSQL:** Store records with a unique constraint on first and last name.
- **Docker Compose:** Build and run the stack with persistent database storage.

## Tech Stack

| Component | Technology |
| --- | --- |
| Applications | Python 3.12, Flask 3.0.0 |
| Database adapter | psycopg2-binary 2.9.9 |
| Database | PostgreSQL 16 Alpine |
| Reverse proxy | Nginx Alpine |
| Orchestration | Docker Compose |

## Architecture

| Service | Role | Host access |
| --- | --- | --- |
| `proxy` | Nginx reverse proxy | Ports 8080 and 8081 |
| `app_b` | Add records | Through Nginx on port 8080 |
| `app_c` | List and delete records | Through Nginx on port 8081 |
| `db` | Shared database | No published host port |

Nginx forwards host port **8080** to `app_b:80` and host port **8081** to `app_c:80`. Both applications connect to the database using the Compose service name `db`.

The applications and database share `private_net`. The proxy joins both `public_net` and `private_net`. Only the proxy publishes host ports. Network names describe their roles; `private_net` is not configured with `internal: true`.

## Project Structure

```text
containerized-apps/
├── app_b/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── app_c/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── db/
│   └── init.sql
├── proxy/
│   └── nginx.conf
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Git
- Docker Engine with Docker Compose v2, or Docker Desktop
- Available host ports 8080 and 8081

### 1. Clone the repository

```bash
git clone https://github.com/xtilda/containerized-apps.git
cd containerized-apps
```

### 2. Correct the database healthcheck

The current Compose file uses `CMP-SHELL` and references `myuser` in its database healthcheck. Before starting the stack, replace `db.healthcheck.test` with:

```yaml
test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
```

The services use short-form `depends_on`, which controls startup order but does not wait for PostgreSQL to become healthy. Allow the database to finish initializing before submitting requests.

### 3. Build and start

```bash
docker compose up --build -d
```

### 4. Open the applications

- **Add records:** [http://localhost:8080](http://localhost:8080)
- **List and delete records:** [http://localhost:8081](http://localhost:8081)

### Example Workflow

1. Open Service B and submit a first and last name.
2. Open or refresh Service C to see the saved record.
3. Submit the same name again in Service B to see the duplicate-record message.
4. Delete the record in Service C to see the remaining record count.

## Routes

The applications return HTML pages and accept form data.

| Application | Method | Route | Description |
| --- | --- | --- | --- |
| Service B | GET | `/` | Display the add-person form |
| Service B | POST | `/submit` | Submit `first_name` and `last_name` |
| Service C | GET | `/` | List all records ordered by ID |
| Service C | POST | `/delete` | Delete a record using its `id` |

## Database and Configuration

The `people` table is created by `db/init.sql`.

| Column | Type | Details |
| --- | --- | --- |
| `id` | SERIAL | Primary key |
| `first_name` | TEXT | Required |
| `last_name` | TEXT | Required |
| `created_at` | TIMESTAMPTZ | Defaults to the insertion time |

A unique constraint on `(first_name, last_name)` prevents duplicate name pairs.

Both applications receive `DB_HOST`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` through Docker Compose. PostgreSQL uses the corresponding `POSTGRES_*` initialization variables. The demo database is named `appdb`, with user `appuser`.

Database files persist in the `db_data` named volume. The initialization script runs when PostgreSQL initializes an empty data directory; editing it does not automatically update an existing database.

## Useful Commands

Check service status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Open a PostgreSQL session:

```bash
docker compose exec db psql -U appuser -d appdb
```

Stop and remove containers while keeping database data:

```bash
docker compose down
```

Reset the stack and delete stored database records:

```bash
docker compose down -v
docker compose up --build -d
```

**Warning:** `docker compose down -v` removes the database volume and its data.

## Troubleshooting

- **Compose fails during startup:** Check that the healthcheck uses `CMD-SHELL`, as shown above.
- **Database connection errors:** Inspect `docker compose logs db` and wait until PostgreSQL is ready.
- **Port already in use:** Change the host side of the port mapping, for example `"8082:80"`.
- **Schema changes are not applied:** Apply changes manually through PostgreSQL, or reset the volume if existing data is disposable.

## Scope

This project is intended for local learning and demonstration. It uses Flask's development server and hardcoded demo database credentials. Authentication, CSRF protection, comprehensive input validation, and safe HTML rendering are not implemented. Production deployment requires additional work in these areas.
