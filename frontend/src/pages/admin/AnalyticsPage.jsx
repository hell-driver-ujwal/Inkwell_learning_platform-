/** Anonymous page counts with accessible native bar visualizations. */
import { useResource } from "../../hooks/useResource";
import { ResourceState } from "../../components/Feedback";
export default function AnalyticsPage() {
  const resource = useResource("admin/analytics/");
  return (
    <>
      <h1>Page analytics</h1>
      <p>Page, role and date only. No names or IP addresses.</p>
      <ResourceState resource={resource}>
        {(data) => (
          <>
            <h2>Popular pages</h2>
            {data.pages.map((page) => (
              <div className="chart-row" key={page.path}>
                <span>{page.path}</span>
                <meter
                  min="0"
                  max={Math.max(...data.pages.map((entry) => entry.count), 1)}
                  value={page.count}
                />
                <b>{page.count}</b>
              </div>
            ))}
            <h2>By role</h2>
            {data.roles.map((role) => (
              <p key={role.viewer_role}>
                {role.viewer_role}: {role.count}
              </p>
            ))}
            <h2>By day</h2>
            {data.days.map((day) => (
              <p key={day.day}>
                {day.day}: {day.count}
              </p>
            ))}
          </>
        )}
      </ResourceState>
    </>
  );
}
