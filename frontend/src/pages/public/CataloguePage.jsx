/** Search and subject filters map directly to the catalogue API. */
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useResource } from "../../hooks/useResource";
import { ResourceState } from "../../components/Feedback";
import CourseCard from "../../components/CourseCard";
import Field from "../../components/Field";
export default function CataloguePage() {
  const [params, setParams] = useSearchParams();
  const [search, setSearch] = useState(params.get("search") || "");
  const courses = useResource(`courses/?${params}`);
  const subjects = useResource("subjects/", { all: true });
  function searchCourses(event) {
    event.preventDefault();
    setParams({ ...Object.fromEntries(params), search, page: 1 });
  }
  return (
    <>
      <div className="page-heading">
        <span className="eyebrow">THE COURSE LIBRARY</span>
        <h1>Find your next beginning.</h1>
        <p>Explore something new. Practise it. Make it yours.</p>
      </div>
      <form className="filter-bar" onSubmit={searchCourses}>
        <Field
          label="Search courses"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="What would you like to learn?"
        />
        <Field
          label="Subject"
          as="select"
          value={params.get("subject") || ""}
          onChange={(event) =>
            setParams({
              ...Object.fromEntries(params),
              search,
              subject: event.target.value,
              page: 1,
            })
          }
        >
          <option value="">All subjects</option>
          {subjects.data?.results.map((subject) => (
            <option value={subject.id} key={subject.id}>
              {subject.name}
            </option>
          ))}
        </Field>
        <Field
          label="Price"
          as="select"
          value={params.get("is_paid") || ""}
          onChange={(event) =>
            setParams({
              ...Object.fromEntries(params),
              is_paid: event.target.value,
              page: 1,
            })
          }
        >
          <option value="">All courses</option>
          <option value="false">Free courses</option>
          <option value="true">Paid courses</option>
        </Field>
        <button>Search</button>
      </form>
      <ResourceState resource={courses}>
        {(data) => (
          <>
            <p className="muted">{data.count} courses to explore</p>
            <div className="course-grid">
              {data.results.map((course) => (
                <CourseCard key={course.id} course={course} />
              ))}
            </div>
            {!data.count && <p>No courses match your search.</p>}
            <div className="actions">
              {data.previous && (
                <button
                  onClick={() =>
                    setParams({
                      ...Object.fromEntries(params),
                      page: Number(params.get("page") || 1) - 1,
                    })
                  }
                >
                  Previous
                </button>
              )}
              {data.next && (
                <button
                  onClick={() =>
                    setParams({
                      ...Object.fromEntries(params),
                      page: Number(params.get("page") || 1) + 1,
                    })
                  }
                >
                  Next
                </button>
              )}
            </div>
          </>
        )}
      </ResourceState>
    </>
  );
}
