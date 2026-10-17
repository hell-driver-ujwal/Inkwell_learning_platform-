/** Route composition only; page behavior belongs in pages and features. */
import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { Loading } from "./components/Feedback";
import SiteLayout from "./layouts/SiteLayout";
import HomePage from "./pages/public/HomePage";
import CataloguePage from "./pages/public/CataloguePage";
import CourseDetailPage from "./pages/public/CourseDetailPage";
import {
  LoginChoicePage,
  LoginPage,
  RegisterPage,
} from "./pages/public/AuthPages";
import HelpPage from "./pages/public/HelpPage";
import ContactPage from "./pages/public/ContactPage";
import InfoPage from "./pages/public/InfoPage";
import DashboardPage from "./pages/learner/DashboardPage";
import LessonPage from "./pages/learner/LessonPage";
import ActivityPage from "./pages/learner/ActivityPage";
import {
  BookmarksPage,
  CertificatePage,
  MyCoursesPage,
  ResultDetailPage,
  ResultsPage,
} from "./pages/learner/HistoryPages";
import { PaymentPage, PaymentsPage } from "./pages/learner/PaymentPages";
import { PasswordPage, ProfilePage } from "./pages/learner/ProfilePages";
import CourseStudioPage from "./pages/teacher/CourseStudioPage";
import CourseBuilderPage, {
  CourseLearnersPage,
} from "./pages/teacher/CourseBuilderPage";
import LessonEditorPage from "./pages/teacher/LessonEditorPage";
import ActivityEditorPage from "./pages/teacher/ActivityEditorPage";
import AdminHomePage from "./pages/admin/AdminHomePage";
import UsersPage from "./pages/admin/UsersPage";
import ContentAdminPage from "./pages/admin/ContentAdminPage";
import OversightPage from "./pages/admin/OversightPage";
import AnalyticsPage from "./pages/admin/AnalyticsPage";
function RequireSession({ roles }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <Loading />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.must_change_password && location.pathname !== "/password")
    return <Navigate to="/password" replace />;
  if (roles && !roles.includes(user.role))
    return <p role="alert">This workspace is not available to your account.</p>;
  return <Outlet />;
}
export default function App() {
  const { loading } = useAuth();
  if (loading) return <Loading />;
  return (
    <Routes>
      <Route element={<SiteLayout />}>
        <Route index element={<HomePage />} />
        <Route path="courses" element={<CataloguePage />} />
        <Route path="courses/:id" element={<CourseDetailPage />} />
        <Route path="lessons/:id" element={<LessonPage />} />
        <Route path="login" element={<LoginChoicePage />} />
        <Route path="login/:role" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="help" element={<HelpPage />} />
        <Route path="contact" element={<ContactPage />} />
        <Route element={<RequireSession />}>
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="activities/:id" element={<ActivityPage />} />
          <Route path="results" element={<ResultsPage />} />
          <Route path="results/:id" element={<ResultDetailPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="password" element={<PasswordPage />} />
        </Route>
        <Route element={<RequireSession roles={["Learner"]} />}>
          <Route path="my-courses" element={<MyCoursesPage />} />
          <Route path="bookmarks" element={<BookmarksPage />} />
          <Route path="payments" element={<PaymentsPage />} />
          <Route path="payments/:id" element={<PaymentPage />} />
          <Route path="courses/:id/certificate" element={<CertificatePage />} />
        </Route>
        <Route element={<RequireSession roles={["Teacher", "Admin"]} />}>
          <Route path="author/courses" element={<CourseStudioPage />} />
          <Route path="author/courses/:id" element={<CourseBuilderPage />} />
          <Route
            path="author/courses/:id/learners"
            element={<CourseLearnersPage />}
          />
          <Route path="author/lessons/:id" element={<LessonEditorPage />} />
          <Route
            path="author/activities/:id"
            element={<ActivityEditorPage />}
          />
        </Route>
        <Route element={<RequireSession roles={["Admin"]} />}>
          <Route path="admin" element={<AdminHomePage />} />
          <Route path="admin/users" element={<UsersPage />} />
          <Route path="admin/analytics" element={<AnalyticsPage />} />
          {["courses", "activities", "messages", "payments"].map((kind) => (
            <Route
              key={kind}
              path={`admin/${kind}`}
              element={<OversightPage key={kind} kind={kind} />}
            />
          ))}
          <Route path="admin/:resource" element={<ContentAdminPage />} />
        </Route>
        <Route path=":page" element={<InfoPage />} />
        <Route path="*" element={<p>Page not found.</p>} />
      </Route>
    </Routes>
  );
}
