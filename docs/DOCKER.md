# Docker, step by step

## Why the application was already working

During the rebuild, Codex started three ordinary processes on your Mac:

- PostgreSQL on port **55439**, with database files in `.postgres/`.
- Django on port **8000**, using Python packages in `.venv/`.
- Vite on port **5173**, using packages in `frontend/node_modules/`.

The schema had already been migrated and the demonstration dataset imported. The browser was talking to those running processes. Django does not start PostgreSQL automatically, and opening this folder does not start the application. After those processes stop or the computer restarts, you must start them again.

Docker provides another way to run the same source. An **image** is a packaged runtime and dependencies. A **container** is a running instance of that image. **Compose** describes how our three containers connect. A **volume** preserves database files when a container is replaced.

## 1. Open Docker Desktop

Open Docker Desktop from Applications and wait until its engine is running. In Terminal:

```bash
docker version
docker compose version
```

`docker version` should show both Client and Server information. A message about not connecting to `docker.sock` means Docker Desktop's engine is not running yet.

## 2. Open this project in Terminal

```bash
cd /Users/ujjwalchhetri/Desktop/Learning_System_with_django
```

Run the following commands here, where `compose.yaml` is located. You do not activate `.venv` for Docker commands.

## 3. Check the configuration and build the images

```bash
docker compose config --quiet
docker compose build
```

The first build downloads Python, Node and PostgreSQL images as needed and installs dependencies. Subsequent builds reuse cached layers. `backend/Dockerfile` installs Python requirements; `frontend/Dockerfile` installs the npm lockfile. `.dockerignore` keeps host environments, database files and private media out of the image build context.

## 4. Start PostgreSQL

```bash
docker compose up -d db --wait
```

`-d` means detached: keep running in the background. `--wait` waits for the configured health check. The `db` service is reachable by other containers as `db:5432`; it is not exposed as a port on your Mac.

The database credentials in Compose are local teaching defaults. This setup is for development, not production hosting.

## 5. Apply Django migrations

```bash
docker compose run --rm backend python manage.py migrate
```

`run` starts a one-off backend container, executes the command, and `--rm` removes that temporary container when it finishes. The database survives in its named volume.

Migrations create/update the database tables. They do not import course content. We deliberately do not hide migrations or seeding in the container startup command.

## 6. Import the demonstration data once

For the **first setup of an empty Docker database**:

```bash
docker compose run --rm backend python manage.py import_legacy_demo
docker compose run --rm backend python manage.py audit_media
```

The existing workspace already has the copied files in `backend/private_media/legacy/`, which the backend bind mount makes available inside the container. The import reads `data/legacy_seed.json` and creates demo records. It refuses to overwrite a database containing users.

If you see “Database already contains users,” the import has already been done. Do not reset the database; proceed to the next step.

For a fresh copy of the source **without media**, first copy the original assets explicitly:

```bash
mkdir -p backend/private_media/legacy
cp -R /Users/ujjwalchhetri/Downloads/LearningSystem/Uploads/. backend/private_media/legacy/
```

This copies files only. It does not change the original project. Run `audit_media` again afterward.

**The Docker database is separate from the existing local database.** This seed import does not transfer learning activity you subsequently recorded in the local app. A complete transfer of that current database would use an explicit PostgreSQL export/import. Both development modes currently share the same private media folder on the Mac.

## 7. Start Django and React

```bash
docker compose up -d backend frontend
docker compose ps
```

Open **http://127.0.0.1:5174**.

| Service | In the container | On your Mac |
| --- | --- | --- |
| frontend | Vite on 5173 | http://127.0.0.1:5174 |
| backend | Django on 8000 | http://127.0.0.1:8001/api/ |
| db | PostgreSQL on 5432 | Internal Docker network only |

Use the frontend address for normal use. Its `/api/` requests are proxied to `http://backend:8000`. Inside a container, `localhost` refers to that container itself; this is why the backend connects to `db`, and Vite connects to `backend`.

Django trusts the frontend origin for CSRF. Session cookies are still handled by Django, and the browser sees a same-origin application. Cookies are not isolated by port, so Compose gives the Docker session and CSRF cookies distinct names. This keeps its login separate from the existing local app.

Demo login: learner **anita.karki@inkwell.test**, password **Password123**. The README lists lecturer and administrator accounts.

## 8. Read logs and run checks

```bash
docker compose logs --tail=50 backend frontend
docker compose logs -f backend
```

Press Ctrl+C to stop following logs; the detached containers keep running.

```bash
docker compose exec backend python manage.py check
docker compose exec backend python manage.py test --noinput
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
```

`exec` runs a command in an already-running container. Django tests use a temporary PostgreSQL database; they do not reset the demo database.

## 9. Stop and start on another day

```bash
docker compose stop
```

Then, after opening Docker Desktop another day:

```bash
docker compose up -d
```

You do **not** repeat the seed import. Run migrations again only when new migration files have been added.

`docker compose down` removes this project's containers and network while retaining its named database volume. Avoid `docker compose down -v`: the `-v` flag deletes the database volume and its saved learning history. There is no automatic restart policy; these containers start when you ask Compose to start them.

## Editing code

Backend source and frontend `src/` are bind-mounted, so saved code changes trigger Django/Vite reloads. Python packages and Linux `node_modules` stay inside the images. After changing `requirements.txt` or `package-lock.json`, run:

```bash
docker compose up -d --build
```

After changing Django models, generate and inspect migrations:

```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

Generated migration files appear in your workspace because the backend directory is bind-mounted. Never copy the Mac's `.venv` or `node_modules` into a Linux container.

## Files to study

1. `compose.yaml`: services, environment variables, ports, mounts and startup dependency.
2. `backend/Dockerfile`: how the Python runtime is packaged.
3. `frontend/Dockerfile`: how the Node runtime is packaged.
4. `frontend/vite.config.js`: the environment-driven backend proxy.
5. `backend/config/settings/__init__.py`: database settings read from environment variables.

Official references: [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/) and [one-off commands with compose run](https://docs.docker.com/reference/cli/docker/compose/run/).
