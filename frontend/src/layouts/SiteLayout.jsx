/** Public navigation and role workspace links, with keyboard shortcuts. */
import { useEffect } from "react";
import {
  Link,
  NavLink,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";
import { ErrorMessage } from "../components/Feedback";
export default function SiteLayout() {
  const { user, signOut, error } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  useEffect(() => {
    function shortcut(event) {
      if (!event.altKey) return;
      const destination = {
        h: "/",
        c: "/courses",
        d: "/dashboard",
        q: "/help",
      }[event.key.toLowerCase()];
      if (destination) {
        event.preventDefault();
        navigate(destination);
      }
    }
    window.addEventListener("keydown", shortcut);
    return () => window.removeEventListener("keydown", shortcut);
  }, [navigate]);
  useEffect(() => {
    if (!user?.must_change_password) {
      api("page-views/", {
        method: "POST",
        body: { path: location.pathname },
      }).catch((failure) =>
        console.warn("Page count was not recorded:", failure.message),
      );
    }
    window.scrollTo(0, 0);
  }, [location.pathname, user?.must_change_password]);
  async function handleLogout() {
    await signOut();
    navigate("/");
  }
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <Link className="brand" to="/">
          inkwell<span>LEARN BY DOING</span>
        </Link>
        <nav aria-label="Main">
          <NavLink to="/courses">Explore courses</NavLink>
          <NavLink to="/about">About</NavLink>
          <NavLink to="/help">Help</NavLink>
          {user ? (
            <>
              <NavLink to="/dashboard">My workspace</NavLink>
              <button className="text-button" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login">Log in</NavLink>
              <Link className="button small" to="/register">
                Start learning
              </Link>
            </>
          )}
        </nav>
      </header>
      {user && (
        <nav className="workspace-nav" aria-label="Workspace">
          <span>{user.full_name}</span>
          <NavLink to="/dashboard">Dashboard</NavLink>
          {user.role === "Learner" && (
            <>
              <NavLink to="/my-courses">My courses</NavLink>
              <NavLink to="/results">Results</NavLink>
              <NavLink to="/bookmarks">Bookmarks</NavLink>
              <NavLink to="/payments">Payments</NavLink>
            </>
          )}
          {["Teacher", "Admin"].includes(user.role) && (
            <>
              <NavLink to="/author/courses">Course studio</NavLink>
              <NavLink to="/results">Learner results</NavLink>
            </>
          )}
          {user.role === "Admin" && (
            <NavLink to="/admin">Administration</NavLink>
          )}
          <NavLink to="/profile">Profile</NavLink>
        </nav>
      )}
      <main id="main" className="page">
        <ErrorMessage>{error}</ErrorMessage>
        <Outlet />
      </main>
      <footer>
        <div>
          <Link className="brand" to="/">
            inkwell
          </Link>
          <p>Small lessons. Real understanding.</p>
        </div>
        <nav aria-label="Footer">
          <Link to="/contact">Contact</Link>
          <Link to="/privacy">Privacy</Link>
          <Link to="/terms">Terms</Link>
          <Link to="/sitemap">Site map</Link>
        </nav>
        <p className="muted">Made for curious minds. Built to keep learning.</p>
      </footer>
    </>
  );
}
