"""Connectivity specialist: DNS, DHCP and Wi-Fi only.

Wired interface errors/link flaps are owned by Infrastructure Agent.
Performance metrics are never forwarded to this agent's LLM prompt.
"""
from app.config.thresholds import THRESHOLDS

CONNECTIVITY_FIELDS = (
    "device_id", "hostname", "service", "status",
    "signal_strength_dbm", "retransmissions",
    "query_failures", "lease_failures",
)

def _num(row, key):
    try:
        value = row.get(key)
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None

def _present(row, key):
    return row.get(key) not in (None, "")

def _project(row):
    return {k: row[k] for k in CONNECTIVITY_FIELDS if k in row and row[k] not in (None, "")}

def analyze_connectivity(records):
    findings, evidence, affected = [], [], set()
    projected = [_project(r) for r in records]
    meaningful = [r for r in projected if any(
        _present(r, k) for k in CONNECTIVITY_FIELDS[2:]
    )]
    has_metrics = bool(meaningful)

    for r in meaningful:
        device = str(r.get("device_id") or r.get("hostname") or "unknown-device")
        service = str(r.get("service", "")).strip().upper()
        status = str(r.get("status", "")).strip().lower()
        signal = _num(r, "signal_strength_dbm")
        retrans = _num(r, "retransmissions")
        qfail = _num(r, "query_failures")
        lfail = _num(r, "lease_failures")

        if service == "DNS" and (status in {"unreachable", "failed", "down"} or
                (qfail is not None and qfail > THRESHOLDS["dns_query_failures"])):
            findings.append(f"{device}: DNS service failure indicators detected")
            evidence.append({"device_id": device, "metric": "DNS status/query_failures",
                             "value": status or qfail})
            affected.add(device)
        if service == "DHCP" and (status in {"unreachable", "failed", "down", "degraded"} or
                (lfail is not None and lfail > THRESHOLDS["dhcp_lease_failures"])):
            findings.append(f"{device}: DHCP service degradation indicators detected")
            evidence.append({"device_id": device, "metric": "DHCP status/lease_failures",
                             "value": status or lfail})
            affected.add(device)
        if signal is not None and signal <= THRESHOLDS["wifi_signal_dbm"]:
            findings.append(f"{device}: weak Wi-Fi signal ({signal:g} dBm)")
            evidence.append({"device_id": device, "metric": "signal_strength_dbm",
                             "value": signal, "threshold": f'<= {THRESHOLDS["wifi_signal_dbm"]} dBm'})
            affected.add(device)
        if retrans is not None and retrans >= THRESHOLDS["wifi_retransmissions"]:
            findings.append(f"{device}: elevated Wi-Fi retransmissions ({retrans:g})")
            evidence.append({"device_id": device, "metric": "retransmissions",
                             "value": retrans, "threshold": THRESHOLDS["wifi_retransmissions"]})
            affected.add(device)

    if not has_metrics:
        llm = {"provider": "groq", "status": "skipped",
               "message": "Connectivity telemetry is absent; AI interpretation skipped to prevent unsupported conclusions."}
        agent_status = "insufficient_data"
    else:
        from app.llm.groq_service import analyze_with_groq
        llm = analyze_with_groq(
            "Connectivity Agent",
            "Interpret only DNS, DHCP and Wi-Fi signal/retransmission indicators. "
            "Do not infer latency, packet loss, utilization, CPU, memory or wired interface health.",
            {"connectivity_telemetry": meaningful[:50], "findings": findings, "evidence": evidence,
             "available_connectivity_fields": sorted({k for row in meaningful for k in row.keys()})},
            ["summary", "possible_impacts", "follow_up_checks"])
        agent_status = "findings" if findings else "clear"

    return {"agent": "connectivity_agent", "status": agent_status,
            "findings": findings, "evidence": evidence,
            "affected_devices": sorted(affected), "llm_analysis": llm}
