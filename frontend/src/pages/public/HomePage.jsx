/** A welcoming entry into the original Inkwell course catalogue. */
import { Link } from "react-router-dom";
import { useResource } from "../../hooks/useResource";
import CourseCard from "../../components/CourseCard";
import { ResourceState } from "../../components/Feedback";
export default function HomePage() {
  const courses = useResource("courses/");
  return (
    <>
      <section className="hero">
        <div>
          <span className="eyebrow">A LITTLE CURIOSITY GOES A LONG WAY</span>
          <h1>
            Learn something.
            <br />
            <em>Make it yours.</em>
          </h1>
          <p>
            Clear lessons, playful practice and real progress.
            <br />A space to build skills at your own pace.
          </p>
          <div className="actions">
            <Link className="button" to="/courses">
              Explore the courses ↗
            </Link>
            <Link to="/about">Meet Inkwell →</Link>
          </div>
          <div className="hero-note">
            19 courses · 8 subjects · Endless beginnings
          </div>
        </div>
        <div className="hero-art" aria-hidden="true">
          <span className="art-label">
            THE ART OF
            <br />
            UNDERSTANDING
          </span>
          <div className="book book-one">think.</div>
          <div className="book book-two">try.</div>
          <div className="book book-three">grow.</div>
          <span className="art-star">✳</span>
        </div>
      </section>
      <section className="feature-strip">
        <div>
          <b>01 / Explore</b>
          <p>Find a subject that sparks your curiosity.</p>
        </div>
        <div>
          <b>02 / Practise</b>
          <p>Turn ideas into understanding with hands-on activities.</p>
        </div>
        <div>
          <b>03 / Grow</b>
          <p>See your progress and celebrate each milestone.</p>
        </div>
      </section>
      <section>
        <div className="section-heading">
          <div>
            <span className="eyebrow">YOUR NEXT CHAPTER</span>
            <h2>Fresh from the library</h2>
          </div>
          <Link to="/courses">View all courses →</Link>
        </div>
        <ResourceState resource={courses}>
          {(data) => (
            <div className="course-grid">
              {data.results.slice(0, 6).map((course) => (
                <CourseCard key={course.id} course={course} />
              ))}
            </div>
          )}
        </ResourceState>
      </section>
      <section className="panel">
        <h2>Take a look around</h2>
        <video
          controls
          preload="metadata"
          poster="/assets/video/inkwell-intro-poster.jpg"
        >
          <source src="/assets/video/inkwell-intro.mp4" type="video/mp4" />
          <track
            kind="captions"
            srcLang="en"
            label="English"
            default
            src="/assets/video/inkwell-intro.vtt"
          />
        </video>
      </section>
      <section className="callout">
        <h2>Have something to teach?</h2>
        <p>Share what you know. Help someone take their first step.</p>
        <Link className="button" to="/register?role=Teacher">
          Apply to be a lecturer
        </Link>
      </section>
    </>
  );
}
