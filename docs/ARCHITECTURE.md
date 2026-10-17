# Architecture and implementation plan

The original application at `/Users/ujjwalchhetri/Downloads/LearningSystem` is a read-only reference. This directory is the separate rewrite.

## Source inspection

The SQL schema has 25 tables. The final reproducible SQL seed contains 19 courses, 8 subjects, 72 materials and 73 activities. The MDF database may contain later changes; reading its live contents requires SQL Server. The seed is the portable baseline, not a claim that the MDF was exported.

Rules were traced through the C# access, publishing, payment, progress, scoring, scenario, discussion, upload and account helpers and their Web Forms callers. Source documents describe behavior; they do not authorize running destructive SQL scripts.

## Domain boundaries

- **accounts**: custom email user, roles/status, sessions, lockout, profile and administrative account actions.
- **courses**: catalogue, subjects, course ownership, ordered topics and protected lesson materials.
- **learning**: enrollment, completions, bookmarks, reviews, progress and certificates.
- **activities**: shared curriculum metadata, attempt history and server-owned play sessions. This is shared infrastructure, not a replacement for the distinct activity domains.
- **quizzes**: questions/options, answer validation and weighted scoring.
- **assessments**: confidence statements, ratings and historical comparison.
- **games**: eight templates, content validation and template-specific scoring.
- **scenarios**: steps, choices and validated branching traversal.
- **discussions**: posts, one-level replies, closure and moderation.
- **payments**: local eSewa simulation, receipts and atomic enrollment.
- **support**: public FAQ and CAPTCHA-protected contact messages.
- **analytics**: anonymous page counts and role-specific dashboards.

## Request flow

React page → centralized API client → DRF view → serializer validation → permission/service → Django ORM → PostgreSQL. A serializer describes and validates data. A permission decides who may act. A service implements a business action. A selector assembles a complex read. Views coordinate these pieces.

Use Django sessions and CSRF protection through Vite's same-origin development proxy. Passwords use Django's hashers. Never expose quiz answers in a learner's pre-submission representation. Private files have authorized endpoints, not a public media directory.

## Integrity decisions

Use PostgreSQL transactions and row locks for payment completion, enrollment, play submission and authoring locks. A play session records server time and a content revision; repeated starts cannot reset a timer. Completed attempts freeze activity structure. Leaving a course removes enrollment only. Administrator oversight and author ownership are separate permissions. Previews never create learner attempts.

## Implementation sequence

1. Define models, authentication, permissions and migrations.
2. Implement enrollment, protected content, domain scoring and authoring validation.
3. Import the literal seed safely without executing SQL Server code; copy media.
4. Build public, learner, lecturer and administrator React workflows.
5. Test security and business rules against PostgreSQL, build the frontend, and review readability.

## Learning path

Start with `accounts/models.py`, then follow enrollment from the React course page through the DRF view into `learning/services.py`. Next study quiz scoring and its tests. Read the shared play-session service last: concurrency and idempotency are easier after ordinary request flow is familiar.
