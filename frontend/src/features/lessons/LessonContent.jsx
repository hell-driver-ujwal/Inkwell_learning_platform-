/** Render each lesson format safely; code labs run in an isolated iframe. */
import { useState } from "react";
import ReactMarkdown from "react-markdown";
export default function LessonContent({ lesson }) {
  const [code, setCode] = useState(lesson.text_content);
  const [runningCode, setRunningCode] = useState(lesson.text_content);
  if (lesson.kind === "Text")
    return (
      <article className="reading">
        <ReactMarkdown>{lesson.text_content}</ReactMarkdown>
      </article>
    );
  if (lesson.kind === "Image")
    return (
      <figure>
        <img
          className="lesson-image"
          src={lesson.file_url}
          alt={lesson.alt_text}
        />
        <figcaption>{lesson.alt_text}</figcaption>
      </figure>
    );
  if (lesson.kind === "PDF")
    return (
      <>
        <a href={lesson.file_url} target="_blank" rel="noreferrer">
          Open PDF in a new tab
        </a>
        <iframe
          className="document-frame"
          title={lesson.title}
          src={lesson.file_url}
        />
      </>
    );
  if (lesson.kind === "Video")
    return (
      <>
        <video controls src={lesson.file_url}>
          {lesson.captions_url && (
            <track
              kind="captions"
              srcLang="en"
              label="English"
              default
              src={lesson.captions_url}
            />
          )}
        </video>
        <p className="reading">{lesson.text_content}</p>
      </>
    );
  if (lesson.kind === "Audio")
    return (
      <>
        <audio controls src={lesson.file_url} />
        <p className="reading">{lesson.text_content}</p>
      </>
    );
  if (lesson.kind === "YouTube") {
    const url = new URL(lesson.youtube_url);
    const videoId = url.searchParams.get("v") || url.pathname.slice(1);
    return (
      <iframe
        className="video-frame"
        title={lesson.title}
        src={`https://www.youtube-nocookie.com/embed/${videoId}`}
        allowFullScreen
      />
    );
  }
  if (lesson.kind === "Code")
    return (
      <section className="code-lab">
        <label htmlFor="code-editor">Edit the HTML, CSS and JavaScript</label>
        <textarea
          id="code-editor"
          spellCheck="false"
          value={code}
          onChange={(event) => setCode(event.target.value)}
        />
        <div className="actions">
          <button onClick={() => setRunningCode(code)}>Run code</button>
          <button
            className="secondary"
            onClick={() => {
              setCode(lesson.text_content);
              setRunningCode(lesson.text_content);
            }}
          >
            Reset
          </button>
        </div>
        <iframe
          title="Code lab output"
          sandbox="allow-scripts"
          srcDoc={runningCode}
        />
      </section>
    );
  return <p>This lesson format is unavailable.</p>;
}
