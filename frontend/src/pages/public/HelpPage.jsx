/** Searchable FAQs respect the backend's audience filtering. */
import { useState } from "react";
import { useResource } from "../../hooks/useResource";
import { ResourceState } from "../../components/Feedback";
import Field from "../../components/Field";
export default function HelpPage() {
  const [search, setSearch] = useState("");
  const resource = useResource(`faqs/?search=${encodeURIComponent(search)}`);
  return (
    <section className="reading">
      <h1>A little guidance.</h1>
      <p>Find an answer and get back to learning.</p>
      <Field
        label="Search help"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
      />
      <ResourceState resource={resource}>
        {(data) =>
          data.results.map((faq) => (
            <details key={faq.id}>
              <summary>{faq.question}</summary>
              <p>{faq.answer}</p>
            </details>
          ))
        }
      </ResourceState>
      <h2>Keyboard shortcuts</h2>
      <p>Alt+H: Home · Alt+C: Courses · Alt+D: Dashboard · Alt+Q: Help</p>
    </section>
  );
}
