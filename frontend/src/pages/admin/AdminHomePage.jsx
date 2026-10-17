/** Administrator navigation separates oversight from owned-course authoring. */
import { Link } from "react-router-dom";
const sections = [
  ["users", "Accounts & applications"],
  ["subjects", "Subjects"],
  ["courses", "Course oversight"],
  ["activities", "Activity oversight"],
  ["messages", "Contact messages"],
  ["faqs", "Help & FAQs"],
  ["payments", "Payment history"],
  ["analytics", "Page analytics"],
];
export default function AdminHomePage() {
  return (
    <>
      <span className="eyebrow">ADMINISTRATION</span>
      <h1>Care for the community.</h1>
      <div className="three-columns">
        {sections.map(([path, label]) => (
          <Link key={path} className="panel" to={`/admin/${path}`}>
            <h2>{label}</h2>
            <span>Open →</span>
          </Link>
        ))}
      </div>
    </>
  );
}
