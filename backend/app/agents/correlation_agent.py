"""Evidence correlation; deterministic rules remain the source of the final cause."""
from app.llm.groq_service import analyze_with_groq


def _coverage(records):
    keys = {key for row in records for key, value in row.items() if value not in (None, "")}
    # Generic `status` on a DNS/DHCP row belongs to connectivity, not infrastructure.
    if any(row.get("status") not in (None, "") and not row.get("service") for row in records):
        keys.add("device_status")
    groups = {
        "performance": {"latency_ms", "jitter_ms", "packet_loss_pct", "throughput_mbps", "link_utilization_pct", "queue_drops"},
        "infrastructure": {"device_status", "cpu_usage_pct", "memory_usage_pct", "interface_errors", "link_flaps"},
        "connectivity": {"service", "query_failures", "lease_failures", "signal_strength_dbm", "retransmissions"},
    }
    present = {name: sorted(fields & keys) for name, fields in groups.items()}
    available = [name for name, fields in present.items() if fields]
    missing = [name for name, fields in present.items() if not fields]
    return {"groups": present, "available_groups": available, "missing_groups": missing,
            "coverage_ratio": round(len(available) / len(groups), 2)}


def correlate_findings(agent_results, records=None):
    records = records or []
    evidence = [e for result in agent_results for e in result.get("evidence", [])]
    findings = [f for result in agent_results for f in result.get("findings", [])]
    metrics = {e.get("metric") for e in evidence}
    coverage = _coverage(records)

    if any(isinstance(m, str) and ("DNS" in m or "DHCP" in m) for m in metrics):
        cause = "DNS/DHCP service failure"; rationale = "DNS query failures or DHCP lease failures/status degradation were observed."; base_confidence = 0.93
    elif any(m in metrics for m in {"link_utilization_pct", "queue_drops"}):
        cause = "Link congestion"; rationale = "High link utilization and/or queue drops were observed."; base_confidence = 0.94 if {"link_utilization_pct", "queue_drops"} <= metrics else 0.86
    elif "signal_strength_dbm" in metrics or "retransmissions" in metrics:
        cause = "Weak Wi-Fi signal"; rationale = "Weak signal strength or elevated wireless retransmissions were observed."; base_confidence = 0.90
    elif any(m in metrics for m in {"interface_errors/link_flaps", "interface_errors", "link_flaps"}):
        cause = "Ethernet/interface fault"; rationale = "Interface errors or link flaps indicate a possible wired-link problem."; base_confidence = 0.91
    elif findings:
        cause = "Infrastructure or connectivity degradation (cause uncertain)"; rationale = "Anomalies were observed, but evidence is insufficient to isolate a specific cause."; base_confidence = 0.55
    else:
        cause = "No significant fault detected"; rationale = "No configured anomaly thresholds were crossed in the supplied telemetry."; base_confidence = 0.90

    # Reduce confidence when diagnostic domains are absent. Do not call incomplete coverage healthy.
    confidence = round(base_confidence * (0.70 + 0.30 * coverage["coverage_ratio"]), 2)
    incomplete = bool(coverage["missing_groups"])
    if not findings and incomplete:
        cause = "No fault detected in available telemetry; coverage incomplete"
        missing_names = ", ".join(coverage["missing_groups"])
        available_names = ", ".join(coverage["available_groups"]) or "none"
        rationale = (
            f"No configured thresholds were crossed in available telemetry. "
            f"Available domains: {available_names}. Missing domains: {missing_names}. "
            "Overall network health cannot be confirmed until missing telemetry is collected."
        )
    llm = analyze_with_groq(
        "Fault Correlation Agent",
        "Compare specialist findings, reconcile evidence, and state uncertainty. Do not change the deterministic cause.",
        {
            # Specialist findings/evidence are the compact, relevant representation;
            # sending raw rows again caused unnecessarily large correlation prompts.
            "telemetry_record_count": len(records),
            "telemetry_fields": sorted({key for row in records for key in row.keys()}),
            "coverage": coverage,
            "rule_based_cause": cause,
            "rationale": rationale,
            "confidence_heuristic": confidence,
            "findings": findings[:30],
            "evidence": evidence[:40],
            "agent_statuses": {r.get("agent"): r.get("status") for r in agent_results},
        },
        ["summary", "corroborating_evidence", "uncertainties"])
    if not findings and incomplete and llm.get("status") == "completed":
        output = llm.get("output")
        if isinstance(output, dict):
            output["summary"] = rationale
            output["uncertainties"] = [
                f"Missing telemetry domain: {name}" for name in coverage["missing_groups"]
            ][:10]
    affected = sorted({e.get("device_id") for e in evidence if e.get("device_id")})
    return {"agent": "fault_correlation_agent",
            "status": "findings" if findings else ("insufficient_data" if incomplete else "clear"),
            "findings": findings, "evidence": evidence, "affected_devices": affected,
            "suspected_root_cause": cause, "rationale": rationale, "confidence": confidence,
            "confidence_basis": "heuristic adjusted for telemetry-domain coverage; not calibrated probability",
            "telemetry_coverage": coverage, "llm_analysis": llm}
