/** Informational pages retain the platform's learner-facing purpose. */
import { Link, useParams } from "react-router-dom";
const pages = {
  about: {
    title: "A place for curious minds.",
    paragraphs: [
      "Inkwell brings short lessons and meaningful practice together. Explore programming, science, mathematics, communication and more at your own pace.",
      "Read, listen, watch and experiment. Quizzes, games, code labs and branching scenarios help you put new ideas into practice. Complete every published item in a course to earn a certificate.",
      "Lecturers build and publish their own courses. Applications to teach are reviewed by an administrator.",
    ],
  },
  privacy: {
    title: "Your learning, your privacy.",
    paragraphs: [
      "Your profile, enrollments, progress and submitted work are stored so you can continue learning. Course authors and administrators can review relevant learner results.",
      "Page analytics store only the page path, viewer role and date. They do not store names, IP addresses or tracking cookies. Session cookies are used to keep you signed in and protect forms.",
      "The eSewa checkout is a local demonstration. No real money is transferred. Receipts contain a masked mobile reference. Contact the administrator with account or privacy questions.",
    ],
  },
  terms: {
    title: "Learning together, respectfully.",
    paragraphs: [
      "Use your own account, keep your password private and treat other learners with respect. Share constructive discussion posts and original work.",
      "Course content is provided for learning. Complete quizzes and activities honestly. Flashcards and self-assessments are personal reflections, not formal qualifications.",
      "Demo payments are simulations. Certificates recognize completion of published course content. External YouTube content requires internet access.",
    ],
  },
};
export default function InfoPage() {
  const { page } = useParams();
  if (page === "sitemap")
    return (
      <>
        <h1>Find your way.</h1>
        <ul>
          {[
            "courses",
            "about",
            "help",
            "contact",
            "login",
            "register",
            "privacy",
            "terms",
          ].map((path) => (
            <li key={path}>
              <Link to={`/${path}`}>{path}</Link>
            </li>
          ))}
        </ul>
      </>
    );
  const content = pages[page];
  if (!content)
    return (
      <>
        <h1>Page not found</h1>
        <Link to="/">Return home</Link>
      </>
    );
  return (
    <article className="reading">
      <h1>{content.title}</h1>
      {content.paragraphs.map((text) => (
        <p key={text}>{text}</p>
      ))}
    </article>
  );
}
