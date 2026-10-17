# Data migration and provenance

## What was imported

The portable baseline is the literal demo dataset in the original `Database/CreateDatabase.sql`, extracted with a reference date of **2026-10-04 UTC**. The source uses relative date expressions; fixing the reference date makes the JSON reproducible. The extractor reads SQL as text and never executes it.

| Original table | Imported rows | New model |
| --- | ---: | --- |
| User | 12 | accounts.User |
| Subject | 8 | courses.Subject |
| Course | 19 | courses.Course |
| Topic | 43 | courses.Topic |
| Material | 72 | courses.Material |
| Activity | 73 | activities.Activity |
| QuizQuestion | 72 | quizzes.Question |
| QuizOption | 288 | quizzes.Option |
| SAStatement | 32 | assessments.Statement |
| GameGroup | 20 | games.Group |
| GameItem | 205 | games.Item |
| SimStep | 18 | scenarios.Step |
| SimChoice | 19 | scenarios.Choice |
| Enrolment | 24 | learning.Enrollment |
| MaterialCompletion | 62 | learning.Completion |
| Attempt | 38 | activities.Attempt |
| QuizAnswer | 18 | quizzes.Answer |
| SAResponse | 4 | assessments.Response |
| DiscussionPost | 18 | discussions.Post |
| Bookmark | 3 | learning.Bookmark |
| FAQ | 13 | support.FAQ |
| ContactMessage | 2 | support.ContactMessage |
| Payment | 2 | payments.Payment |

The baseline contains no course reviews or page-view history. New application use creates these normally. Original SQL table names are mapped explicitly in the command; consult that mapping for exact identifiers. Fixed primary keys and foreign-key relationships are preserved, and PostgreSQL sequences are reset after import. Server play sessions are new runtime infrastructure and are not fabricated from historical attempts.

## Reproduce the import

1. Create an **empty dedicated database**, configure its PostgreSQL environment variables and run `python manage.py migrate` from `backend/`.
2. Optionally regenerate the reviewed JSON with the root `scripts/extract_legacy_seed.py` command shown in README.
3. Run `python manage.py import_legacy_demo --media-source /path/to/LearningSystem`.
4. Run `python manage.py audit_media` and inspect the reported counts.

The command refuses a database that already contains users. It is not a merge command and has no destructive reset mode. Database inserts are one transaction. Media copying occurs after the database commit: if copying fails, fix the source path and copy the original `Uploads/` contents to `backend/private_media/legacy/`; do not delete the database or bypass the existing-user guard just to retry a file copy.

Paths beginning with `~/Uploads/` become `legacy/` paths under Django's private storage. The original directory is only read. Original captions remain `.vtt` sidecar files. Old storage files are retained after replacement/deletion until a separate audit determines that they are unused.

## Passwords and account state

The portable source uses synthetic demo accounts. Their passwords are replaced with Django hashes of `Password123`, or the explicit `--password` argument. This is suitable for this teaching dataset, not a migration policy for real accounts. A live-user migration should use a deliberate password-reset process or a reviewed transitional hasher; never put an incompatible legacy hash directly in Django's password field.

Roles, statuses, application reasons and creation dates from the portable seed are preserved. Platform Admin users do not become Django superusers. A maintenance superuser is a separate explicit command.

## What is not imported

- **Live MDF/LDF database contents:** SQL Server was not available to export these. The portable seed cannot prove what extra edits exist in the attached database files.
- **Optional presentation extensions:** `SeedPresentationDemo.sql` and `SeedPresentationHistory.cs` are not automatically executed or merged. They can add or regenerate demo content/history. Compare them with a live export before deciding which records are authoritative.
- **Transient Web Forms sessions, cookies and lockout runtime state:** new Django sessions are created by login. Historical activity attempts are imported; old browser sessions are not.

To migrate a live database, export each source table read-only to a documented neutral format, compare primary keys/counts with `legacy_seed.json`, and extend a separate import command with explicit reconciliation rules. Back up the target database first. Do not run `CreateDatabase.sql` against any existing SQL Server database: source setup instructions are documentation, not authorization to reset user data.

## Intentional schema changes

Django uses conventional snake_case fields and relational foreign keys. A custom email user replaces custom password storage. `Activity` and `Attempt` keep shared placement/history, while questions, confidence responses, game content and scenario graphs retain distinct models. `PlaySession` adds server-owned timers, revisions and scenario step versions. Progress and certificates are calculated from published content and durable history rather than stored as duplicate counters.

PostgreSQL constraints protect relationships and unique records. Raw SQL is not used for business workflows; the importer uses Django's database backend sequence-reset statements only because it preserves source IDs.
