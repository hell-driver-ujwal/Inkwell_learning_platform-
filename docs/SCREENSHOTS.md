# Inkwell feature screenshots

Real browser screenshots of the running React/Django application, captured on **17 October 2026** from a freshly imported, isolated demonstration database. Names, emails, messages and learning records shown here are synthetic demo content. No live user database was used.

Follow [Docker setup](DOCKER.md) or [native setup](LOCAL_SETUP.md) to run these screens yourself. Account credentials are in the [README](../README.md#demo-accounts). Routes below are relative to your frontend address (Docker default: `http://127.0.0.1:5174`). Sign in through the appropriate role portal first.

The gallery covers public pages, account forms, learner workflows, lesson formats, all eight games, branching scenarios, authoring and administration. Expand any image to view it. Screenshots show representative UI states; backend rules such as lockout, authorization and payment idempotency are documented/tested behaviors, not things a static image can prove.

## At a glance

| Course library | Learner dashboard |
| --- | --- |
| ![Searchable course catalogue](screenshots/catalogue.jpg) | ![Learner progress dashboard](screenshots/learner-dashboard.jpg) |

| Course builder | Branching scenario |
| --- | --- |
| ![Lecturer curriculum builder](screenshots/course-builder.jpg) | ![Scenario preview with choices](screenshots/scenario.jpg) |

## Public pages

<details>
<summary>Public home and introduction</summary>

Route: `/`

![Public home and introduction](screenshots/home.jpg)

</details>

<details>
<summary>Searchable course catalogue</summary>

Route: `/courses`

![Searchable course catalogue](screenshots/catalogue.jpg)

</details>

<details>
<summary>Course introduction and free previews</summary>

Route: `/courses/1`

![Course introduction and free previews](screenshots/course-public.jpg)

</details>

<details>
<summary>Separate role portals</summary>

Route: `/login`

![Separate role portals](screenshots/login.jpg)

</details>

<details>
<summary>Learner registration</summary>

Route: `/register`

![Learner registration](screenshots/registration.jpg)

</details>

<details>
<summary>Lecturer application</summary>

Route: `/register?role=Teacher`

![Lecturer application](screenshots/lecturer-registration.jpg)

</details>

<details>
<summary>Frequently asked questions</summary>

Route: `/help`

![Frequently asked questions](screenshots/help.jpg)

</details>

<details>
<summary>Contact form and CAPTCHA</summary>

Route: `/contact`

![Contact form and CAPTCHA](screenshots/contact.jpg)

</details>

<details>
<summary>About the platform</summary>

Route: `/about`

![About the platform](screenshots/about.jpg)

</details>

<details>
<summary>Privacy information</summary>

Route: `/privacy`

![Privacy information](screenshots/privacy.jpg)

</details>

<details>
<summary>Terms information</summary>

Route: `/terms`

![Terms information](screenshots/terms.jpg)

</details>

<details>
<summary>Public site map</summary>

Route: `/sitemap`

![Public site map](screenshots/sitemap.jpg)

</details>

## Learner workspace

<details>
<summary>Learner dashboard and progress</summary>

Route: `/dashboard`

![Learner dashboard and progress](screenshots/learner-dashboard.jpg)

</details>

<details>
<summary>Enrolled courses</summary>

Route: `/my-courses`

![Enrolled courses](screenshots/my-courses.jpg)

</details>

<details>
<summary>Course curriculum and progress</summary>

Route: `/courses/1`

![Course curriculum and progress](screenshots/course-progress.jpg)

</details>

<details>
<summary>Text lesson and navigation</summary>

Route: `/lessons/1`

![Text lesson and navigation](screenshots/text-lesson.jpg)

</details>

<details>
<summary>Image lesson</summary>

Route: `/lessons/2`

![Image lesson](screenshots/image-lesson.jpg)

</details>

<details>
<summary>Editable Code Lab</summary>

Route: `/lessons/3`

![Editable Code Lab](screenshots/code-lab.jpg)

</details>

<details>
<summary>PDF lesson</summary>

Route: `/lessons/8`

![PDF lesson](screenshots/pdf-lesson.jpg)

</details>

<details>
<summary>Audio lesson</summary>

Route: `/lessons/16`

![Audio lesson](screenshots/audio-lesson.jpg)

</details>

<details>
<summary>Timed quiz questions</summary>

Route: `/activities/1`

![Timed quiz questions](screenshots/quiz.jpg)

</details>

<details>
<summary>Confidence self assessment</summary>

Route: `/activities/5`

![Confidence self assessment](screenshots/self-assessment.jpg)

</details>

<details>
<summary>Discussion and replies</summary>

Route: `/activities/6`

![Discussion and replies](screenshots/discussion.jpg)

</details>

<details>
<summary>Private learning history</summary>

Route: `/results`

![Private learning history](screenshots/results.jpg)

</details>

<details>
<summary>Submitted quiz answer review</summary>

Route: `/results/5`

![Submitted quiz answer review](screenshots/quiz-review.jpg)

</details>

<details>
<summary>Confidence history comparison</summary>

Route: `/results/2`

![Confidence history comparison](screenshots/confidence-history.jpg)

</details>

<details>
<summary>Saved lessons</summary>

Route: `/bookmarks`

![Saved lessons](screenshots/bookmarks.jpg)

</details>

<details>
<summary>Printable completion certificate</summary>

Route: `/courses/16/certificate`

![Printable completion certificate](screenshots/certificate.jpg)

</details>

<details>
<summary>Payment history</summary>

Route: `/payments`

![Payment history](screenshots/payments.jpg)

</details>

<details>
<summary>Local demo checkout</summary>

Route: `/courses/5`

![Local demo checkout](screenshots/checkout.jpg)

</details>

<details>
<summary>Profile editing</summary>

Route: `/profile`

![Profile editing](screenshots/profile.jpg)

</details>

<details>
<summary>Password change form</summary>

Route: `/password`

![Password change form](screenshots/password.jpg)

</details>

<details>
<summary>Course review form</summary>

Route: `/courses/1`

![Course review form](screenshots/reviews.jpg)

</details>

## Lecturer workspace

<details>
<summary>Lecturer dashboard</summary>

Route: `/dashboard`

![Lecturer dashboard](screenshots/teacher-dashboard.jpg)

</details>

<details>
<summary>Course studio and create form</summary>

Route: `/author/courses`

![Course studio and create form](screenshots/course-studio.jpg)

</details>

<details>
<summary>Topics and curriculum authoring</summary>

Route: `/author/courses/1`

![Topics and curriculum authoring](screenshots/course-builder.jpg)

</details>

<details>
<summary>Lesson and upload editor</summary>

Route: `/author/lessons/2`

![Lesson and upload editor](screenshots/lesson-editor.jpg)

</details>

<details>
<summary>Activity publication and attempt settings</summary>

Route: `/author/activities/1`

![Activity publication and attempt settings](screenshots/activity-settings.jpg)

</details>

<details>
<summary>Quiz questions and answers editor</summary>

Route: `/author/activities/1`

![Quiz questions and answers editor](screenshots/quiz-editor.jpg)

</details>

<details>
<summary>Confidence statement editor</summary>

Route: `/author/activities/5`

![Confidence statement editor](screenshots/assessment-editor.jpg)

</details>

<details>
<summary>Game content editor</summary>

Route: `/author/activities/2`

![Game content editor](screenshots/game-editor.jpg)

</details>

<details>
<summary>Branching scenario editor</summary>

Route: `/author/activities/13`

![Branching scenario editor](screenshots/scenario-editor.jpg)

</details>

<details>
<summary>Discussion prompt and closure settings</summary>

Route: `/author/activities/6`

![Discussion prompt and closure settings](screenshots/discussion-editor.jpg)

</details>

<details>
<summary>Course learners and progress</summary>

Route: `/author/courses/1/learners`

![Course learners and progress](screenshots/course-learners.jpg)

</details>

<details>
<summary>Author-scoped results</summary>

Route: `/results`

![Author-scoped results](screenshots/teacher-results.jpg)

</details>

## Administration

<details>
<summary>Administrator overview</summary>

Route: `/admin`

![Administrator overview](screenshots/admin-dashboard.jpg)

</details>

<details>
<summary>Accounts and lecturer approvals</summary>

Route: `/admin/users`

![Accounts and lecturer approvals](screenshots/admin-users.jpg)

</details>

<details>
<summary>Subject management</summary>

Route: `/admin/subjects`

![Subject management](screenshots/admin-subjects.jpg)

</details>

<details>
<summary>FAQ management</summary>

Route: `/admin/faqs`

![FAQ management](screenshots/admin-faqs.jpg)

</details>

<details>
<summary>Course oversight</summary>

Route: `/admin/courses`

![Course oversight](screenshots/admin-courses.jpg)

</details>

<details>
<summary>Activity oversight</summary>

Route: `/admin/activities`

![Activity oversight](screenshots/admin-activities.jpg)

</details>

<details>
<summary>Contact inbox</summary>

Route: `/admin/messages`

![Contact inbox](screenshots/admin-messages.jpg)

</details>

<details>
<summary>Receipt oversight</summary>

Route: `/admin/payments`

![Receipt oversight](screenshots/admin-payments.jpg)

</details>

<details>
<summary>Page and role analytics</summary>

Route: `/admin/analytics`

![Page and role analytics](screenshots/analytics.jpg)

</details>

## Games and scenarios

These images use administrator preview mode. Preview runs do not record learner attempts or progress.

<details>
<summary>Matching pairs</summary>

Route: `/activities/2?preview=1`

![Matching pairs](screenshots/matching.jpg)

</details>

<details>
<summary>Sort into groups</summary>

Route: `/activities/3?preview=1`

![Sort into groups](screenshots/sorting.jpg)

</details>

<details>
<summary>Fill in the blank</summary>

Route: `/activities/4?preview=1`

![Fill in the blank](screenshots/fill-blank.jpg)

</details>

<details>
<summary>Timed True/False</summary>

Route: `/activities/7?preview=1`

![Timed True/False](screenshots/true-false.jpg)

</details>

<details>
<summary>Sequence ordering</summary>

Route: `/activities/8?preview=1`

![Sequence ordering](screenshots/sequence.jpg)

</details>

<details>
<summary>Memory pairs</summary>

Route: `/activities/11?preview=1`

![Memory pairs](screenshots/memory.jpg)

</details>

<details>
<summary>Flashcard self-rating</summary>

Route: `/activities/16?preview=1`

![Flashcard self-rating](screenshots/flashcards.jpg)

</details>

<details>
<summary>Word scramble</summary>

Route: `/activities/24?preview=1`

![Word scramble](screenshots/scramble.jpg)

</details>

<details>
<summary>Branching scenario</summary>

Route: `/activities/13?preview=1`

![Branching scenario](screenshots/scenario.jpg)

</details>

## Lesson formats

Text, image, PDF, audio and Code Lab examples also appear under Learner workspace. The seed has no YouTube lesson; that image shows the real editor with YouTube selected, without saving a new lesson or inventing external playback. External YouTube playback requires internet access.

<details>
<summary>Video lesson</summary>

Route: `/lessons/33`

![Video lesson](screenshots/video-lesson.jpg)

</details>

<details>
<summary>YouTube lesson configuration (unsaved editor selection)</summary>

Route: `/author/lessons/2`

![YouTube lesson configuration (unsaved editor selection)](screenshots/youtube-editor.jpg)

</details>

## Reproducing screenshots

Use a separate demo database, not a database containing private user records. Import the bundled seed/media, start the application and sign in with the documented demo accounts. The image manifest in [`screenshots/manifest.json`](screenshots/manifest.json) records each route and caption. Capture at a desktop viewport of 1440 × 1000 for comparable framing.

Activity screenshots require pressing **Start**; author-content screenshots scroll to **Activity content**. Game/scenario previews append `?preview=1`. The checkout screenshot creates only a pending local demo receipt; no real payment is involved. The YouTube editor selection was not saved. The sample dataset's relative dates use the fixed import reference date described in MIGRATION_NOTES.md, so time-sensitive streaks may differ on a later date.

Keep images under `docs/screenshots/` and use relative Markdown links so GitHub, downloaded archives and local Markdown viewers can resolve them. Update the manifest when replacing or adding screenshots. Captures are documentation, not an exhaustive browser regression suite.
