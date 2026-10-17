/** Template-specific labels make the shared item fields understandable to authors. */
import Field from "../../components/Field";
const labels = {
  FillBlank: ["Answer word", "Sentence with one ___ blank"],
  TrueFalse: ["Correct answer: True or False", "Statement"],
  Scramble: ["Word (3–15 letters)", "Hint"],
  Sequence: ["Step text", "Correct position (1, 2, 3…)"],
  Matching: ["Left side", "Matching right side"],
  Memory: ["Front", "Matching back"],
  Flashcards: ["Prompt", "Answer"],
  Sort: ["Item", "Optional note"],
};
export default function GameEditor({ value, onChange, template }) {
  const [textLabel, matchLabel] = labels[template] || labels.Matching;
  function updateItem(index, changes) {
    onChange({
      ...value,
      items: value.items.map((item, position) =>
        position === index ? { ...item, ...changes } : item,
      ),
    });
  }
  return (
    <>
      {template === "Sort" && (
        <section>
          <h3>Groups</h3>
          {value.groups.map((group, index) => (
            <Field
              key={group.key}
              label={`Group ${index + 1}`}
              value={group.name}
              onChange={(event) =>
                onChange({
                  ...value,
                  groups: value.groups.map((entry, position) =>
                    position === index
                      ? { ...entry, name: event.target.value }
                      : entry,
                  ),
                })
              }
            />
          ))}
          <button
            type="button"
            className="secondary"
            onClick={() =>
              onChange({
                ...value,
                groups: [
                  ...value.groups,
                  { key: crypto.randomUUID(), name: "" },
                ],
              })
            }
          >
            Add group
          </button>
        </section>
      )}
      {value.items.map((item, index) => (
        <section className="panel" key={index}>
          <Field
            label={textLabel}
            value={item.text}
            onChange={(event) =>
              updateItem(index, { text: event.target.value })
            }
          />
          <Field
            label={matchLabel}
            value={item.match_text}
            onChange={(event) =>
              updateItem(index, { match_text: event.target.value })
            }
          />
          {template === "Sort" && (
            <Field
              label="Group"
              as="select"
              value={item.group_key || ""}
              onChange={(event) =>
                updateItem(index, { group_key: event.target.value })
              }
            >
              <option value="">Choose a group</option>
              {value.groups.map((group) => (
                <option key={group.key} value={group.key}>
                  {group.name}
                </option>
              ))}
            </Field>
          )}
          <button
            type="button"
            className="text-button"
            onClick={() =>
              onChange({
                ...value,
                items: value.items.filter((_, position) => position !== index),
              })
            }
          >
            Remove item
          </button>
        </section>
      ))}
      <button
        type="button"
        className="secondary"
        onClick={() =>
          onChange({
            ...value,
            items: [
              ...value.items,
              { text: "", match_text: "", group_key: "" },
            ],
          })
        }
      >
        Add item
      </button>
    </>
  );
}
