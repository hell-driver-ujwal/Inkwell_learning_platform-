/** The authenticated user is shared; page-specific state stays in its page. */
import { createContext, useContext, useEffect, useState } from "react";
import * as auth from "../api/auth";
const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    auth
      .getSession()
      .then((session) => setUser(session.user))
      .catch((failure) => setError(failure.message))
      .finally(() => setLoading(false));
  }, []);
  async function signIn(credentials) {
    const session = await auth.login(credentials);
    setUser(session.user);
    return session.user;
  }
  async function signOut() {
    await auth.logout();
    setUser(null);
    await auth.getSession();
  }
  return (
    <AuthContext.Provider
      value={{ user, setUser, loading, error, signIn, signOut }}
    >
      {children}
    </AuthContext.Provider>
  );
}
export const useAuth = () => useContext(AuthContext);
