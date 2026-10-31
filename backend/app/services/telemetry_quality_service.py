"""Data-quality diagnostics for uploaded telemetry."""
import math

NUMERIC_FIELDS = {
    "latency_ms", "jitter_ms", "packet_loss_pct", "throughput_mbps",
    "link_utilization_pct", "queue_drops", "cpu_usage_pct", "memory_usage_pct",
    "interface_errors", "link_flaps", "signal_strength_dbm", "retransmissions",
    "query_failures", "lease_failures",
}
KNOWN_FIELDS = {"device_id", "hostname", "timestamp", "service", "status", *NUMERIC_FIELDS}

def assess_telemetry_quality(records):
    observed = {str(k) for row in records for k in row.keys()}
    invalid = []
    missing_device_rows = 0
    empty_cells = 0
    for index, row in enumerate(records, start=1):
        if not (row.get("device_id") or row.get("hostname")):
            missing_device_rows += 1
        for key, value in row.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                empty_cells += 1
            if key in NUMERIC_FIELDS and value not in (None, ""):
                try:
                    number = float(value)
                    if not math.isfinite(number):
                        raise ValueError()
                except (TypeError, ValueError):
                    invalid.append({"row": index, "field": key})
    warnings = []
    unknown = sorted(observed - KNOWN_FIELDS)
    if unknown: warnings.append("Unrecognized columns are present; they are not used by configured rules.")
    if missing_device_rows: warnings.append(f"{missing_device_rows} row(s) have no device_id or hostname.")
    if invalid: warnings.append(f"{len(invalid)} numeric field value(s) are invalid and may be ignored.")
    if empty_cells: warnings.append(f"{empty_cells} empty cell(s) detected.")
    return {"unknown_columns": unknown, "rows_missing_device_id": missing_device_rows,
            "invalid_numeric_values": invalid, "empty_cell_count": empty_cells,
            "record_count": len(records), "warnings": warnings,
            "quality_status": "warning" if warnings else "good"}
