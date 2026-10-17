# Original feature → Django API → React

This map records implemented counterparts, not a claim that every original browser interaction has been exhaustively regression tested. Paths in the first column are relative to the original LearningSystem. API paths below have the `/api/` prefix. See VERIFICATION.md for actual checks and MIGRATION_NOTES.md for the dataset boundary.

## Public and account workflows

| Original feature/source | Django app and API | React counterpart |
| --- | --- | --- |
| `Default.aspx`, public introduction | courses: `courses/`, `subjects/` | `HomePage`, bundled captioned introduction video |
| `Courses.aspx`, search/subject/paid filtering | courses: `courses/?search=&subject=&is_paid=` | `CataloguePage` |
| `CourseDetails.aspx`, outline and reviews | courses: `courses/{id}/` | `CourseDetailPage`, `CourseCurriculum`, `CourseReviews` |
| `About.aspx`, `Privacy.aspx`, `Terms.aspx`, `SiteMap.aspx` | Static public content | `InfoPage` with public navigation |
| `Help.aspx`, role-specific FAQ | support: `faqs/` | `HelpPage` |
| `Contact.aspx`, CAPTCHA | support: `captcha/`, `contact/` | `ContactPage` |
| `Account/Register.aspx`, learner/lecturer registration | accounts: `auth/register/` | `RegisterPage`; lecturer reason and pending approval |
| Separate learner, lecturer and admin portals | accounts: `auth/login/` with role | `LoginChoicePage`, `LoginPage` |
| Account lockout, forced password change, logout | accounts: `auth/session/`, `auth/password/`, `auth/logout/` | `AuthContext`, route gate, `PasswordPage` |
| Profile name/email editing | accounts: `auth/profile/` | `ProfilePage` |
| `Preview.aspx`, draft/author preview | courses/activities access rules | Course outline, lesson page and activity `?preview=1` |

## Learner content and engagement

| Original feature/source | Django app and API | React counterpart |
| --- | --- | --- |
| `Learner/MyCourses.aspx`, enroll/leave | learning: `my-courses/`, `courses/{id}/enrollment/` | `MyCoursesPage`, `CourseDetailPage` |
| `Learner/CourseHome.aspx`, curriculum progress | courses/learning: `courses/{id}/` | `CourseCurriculum`, progress display |
| Text, Image, PDF, Video, Audio, YouTube and Code Lab lessons | courses: `materials/{id}/` | `LessonPage`, `LessonContent`, sandboxed code output |
| `Media.ashx`, private uploads/captions | courses: `materials/{id}/file/`, `captions/`; scenarios: `scenario-images/{id}/` | Authorized embeds, captions, audio/video byte-range seeking |
| Free lesson previews | courses: publication and `is_preview` checks | Public lesson links, no credit from preview alone |
| Lesson completion and navigation | learning: `materials/{id}/complete/` | `LessonActions`, `LessonNavigation` |
| `Learner/MyBookmarks.aspx` | learning: `bookmarks/`, `materials/{id}/bookmark/` | `BookmarksPage`, bookmark toggle/removal |
| `ReviewHelper.cs` | learning: `courses/{id}/review/` | `CourseReviews`, create/edit/delete own review |
| `Learner/Certificate.aspx` | learning: `courses/{id}/certificate/` | `CertificatePage`, print styling |
| `Learner/Dashboard.aspx`, streak and progress | analytics: `dashboard/` | `DashboardPage` |
| `Learner/MyResults.aspx`, private attempt detail | activities: `attempts/`, `{id}/`, `summary/`, `filters/` | `ResultsPage`, `ResultDetailPage`, summary/filter components |
| `Learner/Checkout.aspx`, local eSewa simulation | payments: `payments/checkout/`, `{id}/verify/`, `{id}/cancel/` | `PaymentPage` |
| `Learner/MyPayments.aspx`, receipts | payments: `payments/`, `{id}/` | `PaymentsPage`, receipt state |

## Distinct activity behaviors

All players use `activities/{id}/` for safe content and `activities/{id}/start/` for a server-owned run. Submission uses `{id}/submit/`, except scenarios use `{id}/move/` and discussions use `posts/`.

| Original behavior | Domain implementation | React component |
| --- | --- | --- |
| Quiz options, weighted marks, timer, attempt limits, answer review | quizzes `scoring.py`; activities service/PlaySession; Question, Option, Answer | `QuizPlayer`, `ActivityResult`, `ResultDetailPage` |
| Self assessment confidence ratings, feedback, previous comparison | assessments Statement/Response and service; activities results | `AssessmentPlayer`, results pages |
| Matching pairs | games Matching validation/scoring | `MatchingGame` |
| Memory pairs and move/time penalty | games Memory scoring | `MemoryGame` |
| Flashcard reveal and known/learning ratings | games Flashcards scoring | `FlashcardGame` |
| Scrambled words and clue | games Scramble scoring | `AnswerGames` |
| Sort into named groups | games Sort scoring | `AnswerGames` |
| Fill blanks, normalized answers | games FillBlank scoring | `AnswerGames` |
| True/False, twelve-second statement countdown | games TrueFalse scoring | `TrueFalseGame` |
| Sequence ordering | games Sequence scoring | `SequenceGame` |
| Branching scenario, step images, Best/Acceptable/Poor ending | scenarios Step/Choice, graph validation and versioned traversal | `ScenarioPlayer` |
| Discussion, one-level reply, own edits/deletes, moderation, closure | discussions Post and service, `posts/?activity={id}` | `Discussion` |

Memory retains the original browser-reported move count; flashcards retain self-rating. These learning activities are not made into a generic quiz or a proctored assessment. Quiz keys are hidden until submission. Author/admin previews never save learner history.

## Authoring and administration

| Original feature/source | Django app and API | React counterpart |
| --- | --- | --- |
| `Teacher/MyCourses.aspx`, `CourseEdit.aspx` | courses: `author/courses/` | `CourseStudioPage`, `CourseForm` |
| `Teacher/CourseBuilder.aspx`, ordered topics | courses: `author/topics/` | `CourseBuilderPage` |
| `Teacher/MaterialEdit.aspx`, media uploads | courses: `author/materials/` | `LessonEditorPage` |
| `Teacher/QuizBuilder.aspx` | activities/quizzes: `author/activities/{id}/content/` | `ActivityEditorPage`, `QuizEditor` |
| `Teacher/SABuilder.aspx` | activities/assessments: same owner content endpoint | `AssessmentEditor` |
| `Teacher/GameBuilder.aspx`, eight templates | activities/games: same owner content endpoint | `GameEditor` |
| `Teacher/ScenarioBuilder.aspx` | activities/scenarios: content endpoint and `{id}/step-image/` | `ScenarioEditor`, `ScenarioImageEditor` |
| `Teacher/DiscussionEdit.aspx`, close/reopen | activities: `author/activities/{id}/` | `ActivityEditorPage` |
| Draft/published state and structural content lock | courses authoring; activities authoring/publishing | Editor status fields and API validation messages |
| Delete eligible course/topic/activity, preserve history | courses `deletion.py` | Course builder and administrator oversight actions |
| `Teacher/CourseLearners.aspx` | courses: `author/courses/{id}/learners/` | `CourseLearnersPage` |
| `Teacher/Results.aspx`, dashboard | activities result scope; analytics `dashboard/` | Shared results and dashboard pages |
| Admin account creation, lecturer approval, rejection, deactivation, unlock/reset | accounts: `admin/users/`, `{id}/action/` | `UsersPage` |
| Admin subject and FAQ maintenance | support: `admin/subjects/`, `admin/faqs/` | `ContentAdminPage` |
| Admin course/activity oversight and unpublish/delete | support: `admin/courses/`, `admin/activities/` | `OversightPage` |
| Admin contact inbox, mark read, email reply | support: `admin/messages/`, `{id}/read/` | `OversightPage`, mailto link |
| Admin receipt inspection | support: `admin/payments/` | `OversightPage` |
| Admin visitor and role analytics | analytics: `page-views/`, `admin/analytics/`, `dashboard/` | `AnalyticsPage`, `AdminHomePage` |

## Cross-cutting rules and delivery boundaries

Backend checks enforce active role, course ownership, publication, enrollment, paid receipts, attempt ownership and results privacy. Session authentication includes CSRF, and passwords use Django hashers. Uploads validate type, size and content signatures; storage paths cannot escape private media. Related saves use transactions, database constraints and critical row locks.

Visible labels, skip navigation, keyboard focus/shortcuts, captions, reduced-motion support, semantic form controls and responsive layouts are implemented. A formal assistive-technology audit and exhaustive browser parity run are not complete. The React visual design and public explanatory copy are reconstructed, not a pixel-for-pixel Web Forms reproduction. Crawler discovery is provided by Django `/robots.txt` and `/sitemap.xml`, including published courses; React pages themselves remain client-rendered.

The SQL demo baseline and bundled media are imported. Live MDF contents and optional presentation dataset extensions remain unimported pending a SQL Server export/comparison. Those are explicit remaining migration boundaries, not silently discarded data.
