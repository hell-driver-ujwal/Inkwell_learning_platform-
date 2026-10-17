"""Extract literal INSERT VALUES data without executing any legacy SQL.

This intentionally supports only the checked-in demo script's literals and
relative DATEADD timestamps. Unknown expressions fail loudly.
"""

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


def split_sql(text, separator=","):
    """Split outside SQL strings and parentheses, preserving escaped quotes."""
    pieces = []
    start = 0
    depth = 0
    quoted = False
    index = 0
    while index < len(text):
        character = text[index]
        if character == "'":
            if quoted and index + 1 < len(text) and text[index + 1] == "'":
                index += 2
                continue
            quoted = not quoted
        elif not quoted:
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
            elif character == separator and depth == 0:
                pieces.append(text[start:index].strip())
                start = index + 1
        index += 1
    pieces.append(text[start:].strip())
    return pieces


def literal(value, reference_date):
    if value.upper() == "NULL":
        return None
    if value.startswith("N'") or value.startswith("'"):
        return value[value.index("'") + 1 : -1].replace("''", "'")
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return value
    if "SYSUTCDATETIME()" in value:
        timestamp = reference_date
        for unit, amount in re.findall(r"DATEADD\((day|minute|second),\s*(-?\d+),", value, re.I):
            timestamp += timedelta(**{unit.lower() + "s": int(amount)})
        return timestamp.isoformat()
    raise ValueError(f"Unsupported SQL literal: {value[:100]}")


def extract(source, reference_date):
    tables = {}
    pattern = r"INSERT dbo\.\[(\w+)\]\s*\(([^)]+)\)\s*VALUES\s*"
    for match in re.finditer(pattern, source):
        table, columns = match.groups()
        columns = re.findall(r"\[(\w+)\]", columns)
        # A semicolon in a lesson string is content, not a statement boundary.
        values_text = split_sql(source[match.end() :], ";")[0]
        rows = tables.setdefault(table, [])
        for row in split_sql(values_text):
            if not row.startswith("(") or not row.endswith(")"):
                raise ValueError(f"Malformed row in {table}")
            values = [literal(value, reference_date) for value in split_sql(row[1:-1])]
            if len(values) != len(columns):
                raise ValueError(f"Column count mismatch in {table}")
            rows.append(dict(zip(columns, values)))
    for step_id, activity_id in re.findall(
        r"UPDATE dbo.Activity SET StartStepID = (\d+) WHERE ActivityID = (\d+)", source
    ):
        for activity in tables["Activity"]:
            if activity["ActivityID"] == int(activity_id):
                activity["StartStepID"] = int(step_id)
    return tables


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--date", default="2026-10-04")
    args = parser.parse_args()
    reference = datetime.fromisoformat(args.date).replace(tzinfo=timezone.utc)
    tables = extract(args.source.read_text(), reference)
    args.output.write_text(json.dumps(tables, indent=2, ensure_ascii=False) + "\n")
    print({table: len(rows) for table, rows in tables.items()})


if __name__ == "__main__":
    main()
