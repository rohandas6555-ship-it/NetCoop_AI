"""Infrastructure specialist: device health, CPU, memory and wired interfaces.

This agent deliberately receives only infrastructure-owned fields. Performance
and DNS/DHCP/Wi-Fi metrics are excluded from its Groq context.
"""
from app.config.thresholds import THRESHOLDS

INFRASTRUCTURE_FIELDS = (
    "device_id", "hostname", "device_status", "cpu_usage_pct", "memory_usage_pct",
    "interface_errors", "link_flaps",
)

def _num(row, key):
    try:
        value = row.get(key)
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None

def _project(row):
    projected = {k: row[k] for k in INFRASTRUCTURE_FIELDS if k in row and row[k] not in (None, "")}
    # `status` is shared by service telemetry (DNS/DHCP) and device telemetry.
    # Treat it as device status only when no service field identifies a service row.
    if not row.get("service") and row.get("status") not in (None, ""):
        projected["device_status"] = row["status"]
    return projected

def analyze_infrastructure(records):
    findings, evidence, affected = [], [], set()
    projected = [_project(r) for r in records]
    meaningful = [r for r in projected if any(
        r.get(k) not in (None, "") for k in INFRASTRUCTURE_FIELDS[2:]
    )]
    has_metrics = bool(meaningful)

    for r in meaningful:
        device = str(r.get("device_id") or r.get("hostname") or "unknown-device")
        status = str(r.get("device_status", "")).strip().lower()
        errors = _num(r, "interface_errors")
        flaps = _num(r, "link_flaps")
        cpu = _num(r, "cpu_usage_pct")
        mem = _num(r, "memory_usage_pct")

        if status in {"down", "failed", "unreachable", "degraded"}:
            findings.append(f"{device}: device status is {status}")
            evidence.append({"device_id": device, "metric": "device_status", "value": status})
            affected.add(device)
        if errors is not None and errors > THRESHOLDS["interface_errors_delta"]:
            findings.append(f"{device}: interface errors detected ({errors:g})")
            evidence.append({"device_id": device, "metric": "interface_errors", "value": errors,
                             "threshold": THRESHOLDS["interface_errors_delta"]})
            affected.add(device)
        if flaps is not None and flaps > THRESHOLDS["link_flaps_delta"]:
            findings.append(f"{device}: link flaps detected ({flaps:g})")
            evidence.append({"device_id": device, "metric": "link_flaps", "value": flaps,
                             "threshold": THRESHOLDS["link_flaps_delta"]})
            affected.add(device)
        if cpu is not None and cpu >= THRESHOLDS["cpu_usage_pct"]:
            findings.append(f"{device}: high CPU usage ({cpu:g}%)")
            evidence.append({"device_id": device, "metric": "cpu_usage_pct", "value": cpu,
                             "threshold": THRESHOLDS["cpu_usage_pct"]})
            affected.add(device)
        if mem is not None and mem >= THRESHOLDS["memory_usage_pct"]:
            findings.append(f"{device}: high memory usage ({mem:g}%)")
            evidence.append({"device_id": device, "metric": "memory_usage_pct", "value": mem,
                             "threshold": THRESHOLDS["memory_usage_pct"]})
            affected.add(device)

    if not has_metrics:
        llm = {"provider": "groq", "status": "skipped",
               "message": "Infrastructure telemetry is absent; AI interpretation skipped."}
        agent_status = "insufficient_data"
    else:
        from app.llm.groq_service import analyze_with_groq
        llm = analyze_with_groq(
            "Infrastructure Agent",
            "Interpret only device status, CPU, memory, interface errors and link flaps. "
            "Do not assess latency, jitter, packet loss, throughput, utilization, queue drops, DNS, DHCP or Wi-Fi.",
            {"infrastructure_telemetry": meaningful[:50], "findings": findings,
             "evidence": evidence,
             "available_infrastructure_fields": sorted({k for row in meaningful for k in row})},
            ["summary", "possible_impacts", "follow_up_checks"])
        agent_status = "findings" if findings else "clear"

    return {"agent": "infrastructure_agent", "status": agent_status,
            "findings": findings, "evidence": evidence,
            "affected_devices": sorted(affected), "llm_analysis": llm}
