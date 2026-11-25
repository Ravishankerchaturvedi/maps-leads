import csv
import io
import json
from pathlib import Path


def detect_format(text):
    stripped = text.lstrip()
    if not stripped:
        return "csv"
    if stripped.startswith("[") or stripped.startswith("{"):
        return "json"
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if first_line.startswith("{") or first_line.startswith("["):
        return "json"
    return "csv"


def _parse_jsonl(text):
    rows = []
    for number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON on line {number}: {error.msg}") from error
        if isinstance(value, dict):
            rows.append(value)
        elif isinstance(value, list):
            rows.extend(item for item in value if isinstance(item, dict))
    return rows


def _parse_json(text):
    stripped = text.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        value = json.loads(stripped)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        return []
    if stripped.startswith("{"):
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            return _parse_jsonl(stripped)
        if isinstance(value, dict):
            for key in ("results", "data", "entries"):
                nested = value.get(key)
                if isinstance(nested, list):
                    return [item for item in nested if isinstance(item, dict)]
            return [value]
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        return []
    return _parse_jsonl(stripped)


def read_rows(path, fmt="auto"):
    text = Path(path).read_text(encoding="utf-8-sig")
    if fmt == "auto":
        fmt = detect_format(text)
    if fmt == "json":
        return _parse_json(text)
    handle = csv.DictReader(io.StringIO(text, newline=""))
    return [dict(row) for row in handle]
