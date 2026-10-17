/** Filters come from visible history, including courses the learner has left. */
import { useResource } from "../../hooks/useResource";
import Field from "../../components/Field";
export default function ResultsFilters({ params, setParams }) {
  const resource = useResource("attempts/filters/");
  const course = params.get("activity__topic__course") || "";
  return (
    <div className="filter-bar">
      <Field
        label="Course"
        as="select"
        value={course}
        onChange={(event) =>
          setParams(
            event.target.value
              ? { activity__topic__course: event.target.value }
              : {},
          )
        }
      >
        <option value="">All courses</option>
        {resource.data?.courses.map((row) => (
          <option
            key={row.activity__topic__course_id}
            value={row.activity__topic__course_id}
          >
            {row.activity__topic__course__title}
          </option>
        ))}
      </Field>
      <Field
        label="Activity"
        as="select"
        value={params.get("activity") || ""}
        onChange={(event) =>
          setParams({
            ...(course ? { activity__topic__course: course } : {}),
            ...(event.target.value ? { activity: event.target.value } : {}),
          })
        }
      >
        <option value="">All activities</option>
        {resource.data?.activities
          .filter(
            (row) =>
              !course || String(row.activity__topic__course_id) === course,
          )
          .map((row) => (
            <option key={row.activity_id} value={row.activity_id}>
              {row.activity__title}
            </option>
          ))}
      </Field>
    </div>
  );
}
