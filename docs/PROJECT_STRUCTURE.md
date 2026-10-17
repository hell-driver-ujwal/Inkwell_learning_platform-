# Finding your way around the project

Start with the root README for installation and the learning path. The original ASP.NET application is outside this directory and remains the reference implementation.

## Top level

| Folder or file | What belongs here |
| --- | --- |
| `backend/` | Django application source and migrations |
| `frontend/` | React source, Vite configuration and npm lockfile |
| `data/legacy_seed.json` | Portable literal seed snapshot, not application configuration |
| `scripts/` | Explicit one-off import preparation and local database setup |
| `docs/` | Architecture, feature mapping, migration notes and verification evidence |
| `.env.example` | Supported environment variable examples; not loaded automatically |
| `pyproject.toml` | Python formatting and lint rules |
| `.venv/` | Generated Python environment; recreate from requirements |
| `.postgres/` | Local development database files; not source code or a portable backup |

## Backend configuration and shared code

`manage.py` is Django's command-line entry point. `config/settings/__init__.py` is the readable environment-driven settings module. A single settings module is sufficient for this project: production-only flags are explicit. `config/urls.py` composes the DRF routers and named action endpoints. `asgi.py` and `wsgi.py` are server entry points.

`common/` contains only genuinely shared infrastructure: publication choices, the DRF error handler, the read-only maintenance admin and test factories. It is not a home for unrelated business logic.

`private_media/` is generated storage. File paths appear in database records, but the directory has no public URL mapping. Authorized views stream the files. Uploaded files and PostgreSQL data should be backed up separately from source code.

## Domain apps

Every app is a normal Django Python package. The important patterns are:

- `models.py`: persisted data, choices, relations, constraints and small model properties.
- `serializers.py`: accepted request fields, validation and response representations.
- `views.py`: HTTP coordination and simple queries.
- `services.py`: business actions and transaction boundaries.
- `selectors.py`: more complicated read queries, where needed.
- `permissions.py`: reusable authorization decisions, where needed.
- `admin.py`: read-only maintenance inspection registrations.
- `migrations/`: versioned schema changes. Commit these alongside model changes.
- `tests/`: behavior-focused Django tests with descriptive names.

Not every app needs every file. Quiz and game HTTP requests share the activity endpoints; their models, validation and scoring remain in their own domain apps.

| App | Files worth opening first |
| --- | --- |
| `accounts/` | `models.py`, `permissions.py`, `services.py`, `authentication.py`, `urls.py` |
| `courses/` | `models.py`, `permissions.py`, `author_views.py`, `services.py`, `deletion.py`, `uploads.py`, `media.py` |
| `learning/` | `services.py` for enrollment; `selectors.py` for calculated progress |
| `activities/` | `models.py`, `services.py`, `authoring.py`, `publishing.py`, `results.py` |
| `quizzes/` | `scoring.py` separates weighted scoring from HTTP and storage |
| `assessments/` | `services.py` computes confidence feedback |
| `games/` | `models.py`, `validation.py`, `scoring.py` distinguish the eight templates |
| `scenarios/` | `services.py` checks each branch transition; `validation.py` checks graph publication |
| `discussions/` | `services.py` owns reply, closure and moderation rules |
| `payments/` | `services.py` owns failed-code persistence and atomic payment/enrollment |
| `support/` | `views.py` for public support; `admin_views.py` for oversight |
| `analytics/` | `selectors.py` for role-scoped dashboard queries |

`courses/management/commands/import_legacy_demo.py` contains explicit field mappings and the transactional import. `audit_media.py` reports storage discrepancies without deleting files.

## Frontend

| Folder | Responsibility |
| --- | --- |
| `src/api/` | Shared cookie/CSRF/error handling and named domain calls |
| `src/context/` | The authenticated session; no general-purpose global store |
| `src/hooks/` | Reusable request lifecycle and stale-response protection |
| `src/components/` | Small shared UI elements, including fields and resource feedback |
| `src/layouts/` | Application frame, navigation and keyboard shortcuts |
| `src/pages/public/` | Public catalogue, login/registration and support pages |
| `src/pages/learner/` | Learning, history, profile and payment screens |
| `src/pages/teacher/` | Course studio and content editor pages |
| `src/pages/admin/` | Account administration and content oversight |
| `src/features/authoring/` | Focused quiz, game, confidence and scenario editors |
| `src/features/games/` | Separate interactive components for game behaviors |
| Other `src/features/` folders | Domain components composed by pages: lesson content, results, reviews, discussion and players |
| `src/styles/` | Responsive layout, typography, focus states and print rules |
| `public/` | Bundled public fonts/licenses and captioned introduction video |

`src/main.jsx` mounts React. `src/App.jsx` composes routes and UI access gates; backend permissions still enforce access. `vite.config.js` proxies API requests in development. `eslint.config.js` checks JavaScript mistakes, and Prettier formats readable source. `dist/` is generated by the build and is not the source to edit.

## Where to add a feature

For a new course action, put request validation in the courses serializer, authorization in its permission rules and the action in a course service. Expose it from the author or public view according to who may use it. Add a focused component or page, call the shared API client, and test the business rule. Do not introduce a new app for one table unless it represents a distinct domain.

## Docker development

`compose.yaml` connects PostgreSQL, Django and Vite. Each application has a `Dockerfile`; `.dockerignore` excludes generated/private host files from images. Read `docs/DOCKER.md` for a command-by-command explanation. Database records persist in a named Docker volume, while source and private media are bind-mounted from this workspace. The original local PostgreSQL cluster is a separate database.
