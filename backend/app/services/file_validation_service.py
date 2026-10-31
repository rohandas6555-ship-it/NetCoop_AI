import csv, io, json

MAX_BYTES = 10 * 1024 * 1024
ALLOWED = {".csv", ".json"}

def validate_telemetry_file(filename: str, content: bytes):
    if len(content) > MAX_BYTES:
        raise ValueError("File exceeds the 10 MB limit.")
    lower = filename.lower()
    if not any(lower.endswith(ext) for ext in ALLOWED):
        raise ValueError("Only CSV and JSON files are supported.")
    if not content.strip():
        raise ValueError("The uploaded file is empty.")
    try:
        text = content.decode("utf-8-sig")
        if lower.endswith(".json"):
            parsed = json.loads(text)
            records = parsed if isinstance(parsed, list) else [parsed]
            if not records or not all(isinstance(row, dict) for row in records):
                raise ValueError("JSON must contain an object or a list of objects.")
            columns = list(records[0].keys())
            count = len(records)
        else:
            reader = csv.DictReader(io.StringIO(text))
            if not reader.fieldnames:
                raise ValueError("CSV header row is missing.")
            columns = reader.fieldnames
            count = sum(1 for _ in reader)
            if count == 0:
                raise ValueError("CSV contains no data rows.")
    except (UnicodeDecodeError, json.JSONDecodeError, csv.Error) as exc:
        raise ValueError("Unable to parse file. Check that it is valid UTF-8 CSV or JSON.") from exc
    return {"record_count": count, "columns": columns, "size_bytes": len(content)}
