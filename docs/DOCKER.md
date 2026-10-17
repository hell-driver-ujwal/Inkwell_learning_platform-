# Run Inkwell with Docker

This guide starts from a fresh GitHub clone or extracted ZIP. Commands run from the folder containing `compose.yaml` and work in PowerShell, macOS Terminal and Linux shells. No Python, Node or PostgreSQL installation is needed on the host.

## 1. Install and start Docker

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for Windows/macOS, or [Docker Engine](https://docs.docker.com/engine/install/) with the [Compose plugin](https://docs.docker.com/compose/install/) on Linux. Start the engine, then check:

```bash
docker version
docker compose version
```

The first command should show both Client and Server. If it cannot connect to the daemon, start Docker Desktop or your Linux Docker service. Use a current Compose version supporting `up --wait`.

## 2. Clone or extract

```bash
git clone https://github.com/hell-driver-ujwal/Inkwell_learning_platform-.git inkwell
cd inkwell
```

For a ZIP download, extract it and open a terminal in the extracted folder instead. Confirm that `README.md`, `compose.yaml`, `backend/`, `frontend/` and `data/` are present. You do not activate a Python virtual environment for Docker commands.

## 3. Build the application images

```bash
docker compose config --quiet
docker compose build
```

An **image** contains a runtime and dependencies. The backend image installs Python requirements; the frontend installs the npm lockfile. The first build downloads dependencies; later builds reuse cached layers. `.dockerignore` excludes host virtual environments, uploads and local database files.

A **container** is a running instance of an image. **Compose** connects the three services described in `compose.yaml`.

## 4. Start PostgreSQL

```bash
docker compose up -d db --wait
```

`-d` leaves it running in the background. `--wait` waits for PostgreSQL's health check. A **named volume** stores database files independently of the container.

The database is reachable by other containers at `db:5432`. It is not exposed on a host port. Compose supplies local demonstration credentials; do not reuse this configuration for a public deployment.

## 5. Create the database tables

```bash
docker compose run --rm backend python manage.py migrate
```

`run` starts a one-off backend container. `--rm` removes that temporary container after the command finishes. Migrations create tables; they do not populate the course library. Database changes are explicit rather than hidden in startup scripts.

## 6. Load the demo and its media once

```bash
docker compose run --rm backend python manage.py import_legacy_demo --media-source /app/data/demo_media
docker compose run --rm backend python manage.py audit_media
```

`data/legacy_seed.json` contains the synthetic accounts, courses, activities and history. `data/demo_media/Uploads/` contains their referenced images, PDFs, audio, videos and captions. Compose mounts `data/` at `/app/data`, so the import path above is **inside the container**, independent of your computer's username or checkout location.

The media audit should report **zero missing files**. The importer refuses to overwrite a database containing users. On subsequent starts, skip it. If you previously imported records without media, copy the bundled assets without touching records:

```bash
docker compose run --rm backend python -c "import shutil; shutil.copytree('/app/data/demo_media/Uploads', '/app/backend/private_media/legacy', dirs_exist_ok=True)"
```

Uploaded files persist in the host folder `backend/private_media/`, which is ignored by Git. The versioned demo media is a separate seed copy. The original ASP.NET application is not required.

## 7. Start the frontend and backend

```bash
docker compose up -d backend frontend
docker compose ps
```

Open **http://127.0.0.1:5174**. Use that same hostname consistently when logging in.

| Service | Container address | Address on your computer |
| --- | --- | --- |
| React/Vite | `frontend:5173` | http://127.0.0.1:5174 |
| Django API | `backend:8000` | http://127.0.0.1:8001/api/ |
| PostgreSQL | `db:5432` | Not exposed |

Vite forwards `/api/` to Django, so the browser uses same-origin cookies and CSRF protection. Inside a container, `localhost` means that container; Django therefore connects to `db`, not `localhost`. Docker session cookie names differ from native development cookie names.

## 8. Sign in and explore

All demo passwords are **Password123**. Choose the corresponding login portal:

| Portal | Email |
| --- | --- |
| Learner | `anita.karki@inkwell.test` |
| Lecturer | `asha.sharma@inkwell.test` |
| Administrator | `admin@inkwell.test` |

The [screenshot tour](SCREENSHOTS.md) shows the main workflows. These are synthetic accounts for local learning. Demo payments do not transfer money: use `9841234567` with code `4567`.

## Daily start, stop and logs

```bash
docker compose up -d
docker compose ps
docker compose logs --tail=50 backend frontend
docker compose logs -f backend
docker compose stop
```

Run the command you need, not the whole block as a startup script. Ctrl+C stops following logs; detached containers keep running. Opening a source folder does not start services automatically.

`docker compose down` removes containers/network but retains the database volume. **`docker compose down -v` deletes that database volume.** Never use it as a routine fix for a seed-import error. Back up database records and `backend/private_media/` before destructive maintenance.

## Update after pulling changes

```bash
git pull
docker compose build
docker compose run --rm backend python manage.py migrate
docker compose up -d
```

Keep your own uncommitted work safe before pulling. Do not rerun the seed importer. Source edits reload through bind mounts; dependency changes require rebuilding the images. Linux dependencies stay inside images, so host `node_modules` and `.venv` are not mounted into containers.

## Tests

With services running:

```bash
docker compose exec backend python manage.py check
docker compose exec backend python manage.py test --noinput
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
```

`exec` runs inside an existing container. Tests use a temporary PostgreSQL database, not the demo database. See [VERIFICATION.md](VERIFICATION.md) for recorded results and limits.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Cannot connect to Docker daemon | Start Docker and rerun `docker version`. |
| Port 5174 or 8001 already allocated | Stop the conflicting application. If changing ports, update Compose's mapping, `PUBLIC_SITE_URL` and `DJANGO_CSRF_TRUSTED_ORIGINS` together. |
| Database table does not exist | Run the migration command in step 5. |
| Empty course library | Import the seed once, as in step 6. |
| Records exist but images/PDFs fail | Use the media-only copy command in step 6 and rerun `audit_media`. |
| “Database already contains users” | The importer protects existing data. Skip it; do not erase the database. |
| CSRF or login error | Use `http://127.0.0.1:5174`, reload the page, and inspect backend logs. |
| Page temporarily unavailable after startup | Check `docker compose ps` and backend/frontend logs; allow the dev servers to finish starting. |
| Changed dependencies are not available | Run `docker compose build`, then `docker compose up -d`. |

The supplied setup runs development servers with debugging enabled. Production needs a separate deployment design, private secrets, HTTPS, backups and a production application server.

Official references: [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/) and [one-off commands](https://docs.docker.com/reference/cli/docker/compose/run/).
