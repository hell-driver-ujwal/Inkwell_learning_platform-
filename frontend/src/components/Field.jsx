/** Visible labels and native validation for ordinary form controls. */
import { useId } from "react";
export default function Field({ label, as = "input", children, ...props }) {
  const id = useId();
  const Control = as;
  return (
    <label className="field" htmlFor={id}>
      <span>{label}</span>
      <Control id={id} {...props}>
        {children}
      </Control>
    </label>
  );
}
