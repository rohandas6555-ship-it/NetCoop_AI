"""Run specialist agents, correlate their evidence, and produce one report."""
from app.agents.performance_agent import analyze_performance
from app.agents.infrastructure_agent import analyze_infrastructure
from app.agents.connectivity_agent import analyze_connectivity
from app.agents.correlation_agent import correlate_findings
from app.agents.recommendation_agent import build_recommendations
from app.services.telemetry_quality_service import assess_telemetry_quality


def _safe_call(agent_name, fn, records):
    try:
        result = fn(records)
        if not isinstance(result, dict):
            raise TypeError("Agent must return a dictionary")
        result.setdefault("agent", agent_name)
        result.setdefault("status", "error")
        result.setdefault("findings", [])
        result.setdefault("evidence", [])
        result.setdefault("affected_devices", [])
        result.setdefault("llm_analysis", {"provider": "groq", "status": "not_run"})
        return result
    except Exception as exc:
        return {"agent": agent_name, "status": "error", "findings": [], "evidence": [],
                "affected_devices": [],
                "error": {"type": type(exc).__name__, "message": "Agent failed; remaining agents continued."},
                "llm_analysis": {"provider": "groq", "status": "error_fallback",
                                 "message": "Agent execution failed; deterministic findings unavailable."}}


def run_diagnosis(records, incident_id, filename, scenario):
    if not isinstance(records, list) or not records or not all(isinstance(r, dict) for r in records):
        raise ValueError("No valid telemetry records were parsed; diagnosis cannot run.")
    specialists = [
        _safe_call("performance_agent", analyze_performance, records),
        _safe_call("infrastructure_agent", analyze_infrastructure, records),
        _safe_call("connectivity_agent", analyze_connectivity, records),
    ]
    correlation = correlate_findings(specialists, records)
    recommendation = build_recommendations(correlation["suspected_root_cause"], correlation["evidence"])
    agent_results = specialists + [correlation, recommendation]

    evidence = correlation["evidence"]
    evidence_devices = sorted({e.get("device_id") for e in evidence if e.get("device_id")})
    affected = sorted({d for a in specialists for d in a.get("affected_devices", [])} | set(evidence_devices))
    coverage = correlation["telemetry_coverage"]
    quality = assess_telemetry_quality(records)
    schema_diagnostics = quality
    has_findings = bool(correlation["findings"])
    if has_findings:
        overall_status = "investigate"
    elif coverage["missing_groups"]:
        overall_status = "insufficient_data"
    else:
        overall_status = "normal"

    llm_statuses = {a["agent"]: a.get("llm_analysis", {}).get("status", "not_run") for a in agent_results}
    completed = sum(v in {"completed", "guarded"} for v in llm_statuses.values())
    skipped = sum(v == "skipped" for v in llm_statuses.values())
    fallback = sum(v in {"error_fallback", "error"} for v in llm_statuses.values())
    total = len(agent_results)
    llm_overall = "completed" if completed == total else ("partial" if completed else ("skipped" if skipped == total else "error_fallback"))

    report = {
      "incident_id": incident_id, "status": overall_status,
      "suspected_root_cause": correlation["suspected_root_cause"],
      "confidence": correlation["confidence"],
      "confidence_type": "heuristic_score_not_calibrated_probability",
      "confidence_basis": correlation["confidence_basis"],
      "affected_devices": affected, "supporting_evidence": evidence,
      "alternative_causes": [] if not has_findings else ["A related upstream or downstream dependency may contribute; topology and event logs are needed to confirm."],
      "recommended_actions": recommendation["recommended_actions"],
      "evidence_sources": [{"file": filename, "scenario_hint": scenario, "records_analyzed": len(records)}],
      "telemetry_coverage": coverage,
      "schema_diagnostics": schema_diagnostics,
      "telemetry_quality": quality,
      "limitations": [
        "Rule-based telemetry checks remain authoritative for measurable findings and root-cause classification.",
        "Groq provides supplementary interpretation and cannot overwrite deterministic classifications.",
        "Confidence is a heuristic score adjusted for telemetry-domain coverage, not a calibrated probability.",
        "Missing telemetry domains limit the ability to confirm overall network health.",
        "No live campus devices, packet captures, topology map or historical baselines were queried."
      ],
      "agent_results": agent_results,
      "llm_analysis": {"provider": "groq", "status": llm_overall, "agent_statuses": llm_statuses},
      "validation": {
        "affected_devices_match_evidence": set(affected) == set(evidence_devices),
        "all_evidence_has_device_id": all(bool(e.get("device_id")) for e in evidence),
        "agent_count": total, "llm_agent_statuses": llm_statuses,
        "llm_completed_count": completed, "llm_skipped_count": skipped, "llm_fallback_count": fallback
      },
      "orchestration": {
        "agents_executed": [a["agent"] for a in agent_results],
        "collaboration": "Specialist agents analyzed normalized telemetry; raw telemetry, findings, evidence and coverage were passed to correlation; the correlated result was passed to recommendations."
      }
    }
    if not 0 <= float(report["confidence"]) <= 1:
        raise ValueError("Final report confidence must be between 0 and 1.")
    if any(not e.get("device_id") for e in evidence):
        raise ValueError("Evidence item missing device_id.")
    return report
