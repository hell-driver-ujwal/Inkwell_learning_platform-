# Run without Docker

Use this route if you want to manage Python, Node and PostgreSQL yourself. The [Docker guide](DOCKER.md) is simpler for a first run. These instructions start from a fresh clone; no database is assumed to exist.

## Prerequisites and source

Install Python 3.14, Node.js 24 (including npm), PostgreSQL 17 and Git using their official installers or your operating system's package manager. Ensure `python`/`python3`, `node`, `npm`, `psql` and `createdb` are available in your terminal. PostgreSQL must be running.

```bash
git clone https://github.com/hell-driver-ujwal/Inkwell_learning_platform-.git inkwell
cd inkwell
```

A downloaded ZIP works too: extract it and open a terminal in its project root.

## Python environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` instead of `python` in the following commands; activation only changes which executable the terminal finds.

With the environment active:

```bash
python -m pip install -r backend/requirements-dev.txt
```

## Create a dedicated PostgreSQL database

Connect as the PostgreSQL administrator created by your installation. For example:

```bash
psql -U postgres -h 127.0.0.1 -d postgres
```

In the SQL prompt, replace the example password with a local password of your choice:

```sql
CREATE ROLE inkwell WITH LOGIN PASSWORD 'choose-a-local-password' CREATEDB;
CREATE DATABASE inkwell OWNER inkwell;
\q
```

`CREATEDB` lets Django create its separate test database. Use a dedicated role/database rather than an unrelated existing database. On installations with a different administrator name, substitute that name for `postgres`.

## Configure this terminal

macOS/Linux:

```bash
export PGHOST=127.0.0.1
export PGPORT=5432
export PGDATABASE=inkwell
export PGUSER=inkwell
export PGPASSWORD='choose-a-local-password'
```

Windows PowerShell:

```powershell
$env:PGHOST = '127.0.0.1'
$env:PGPORT = '5432'
$env:PGDATABASE = 'inkwell'
$env:PGUSER = 'inkwell'
$env:PGPASSWORD = 'choose-a-local-password'
```

Use the password you chose above. Environment variables apply to this terminal and processes launched from it. Repeat them in a new backend terminal. `.env.example` is a reference; Django does **not** automatically read `.env` files.

## Migrate, import and run Django

```bash
cd backend
python manage.py migrate
python manage.py import_legacy_demo --media-source ../data/demo_media
python manage.py audit_media
python manage.py runserver 127.0.0.1:8000
```

Import only once into an empty database. It copies the bundled assets into private storage and creates demo accounts/content. The audit should report zero missing files. Keep this terminal open; Ctrl+C stops Django.

## Run React in another terminal

Open a second terminal in the project root:

```bash
cd frontend
npm ci
npm run dev
```

Open **http://127.0.0.1:5173**. Vite proxies `/api/` to Django on port 8000. The API root alone is not the React application. Use a consistent hostname for cookies. Demo accounts and the password are listed in [README](../README.md#demo-accounts).

## Later starts and updates

Start PostgreSQL, activate the virtual environment, set the database variables, and run Django in one terminal. Run `npm run dev` from `frontend/` in another. Do not repeat the demo import. After pulling changes, install updated requirements, run `npm ci` if the lockfile changed, and apply migrations.

## Testing

From `backend/`, with the virtual environment active and database variables set:

```bash
python manage.py check
python manage.py test --noinput
python manage.py makemigrations --check --dry-run
```

From the repository root, using that same Python environment:

```bash
python -m ruff check backend scripts
python -m ruff format --check backend scripts
```

From `frontend/`:

```bash
npm run lint
npm run format:check
npm run build
```

Tests create a temporary PostgreSQL database. A database-creation permission error means the development role needs `CREATEDB`; do not point tests at a production database.

## Optional isolated cluster helper (macOS/Linux)

`scripts/start_local_postgres.sh` can create a project-local `.postgres/` cluster on port 55439 if PostgreSQL server tools are on PATH. It uses loopback-only trust authentication for local teaching. It is optional, not needed for the dedicated-role setup above, and is not a Windows or production setup script. Follow its printed environment settings and avoid mixing the two database configurations.
