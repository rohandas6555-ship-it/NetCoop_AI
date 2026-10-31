"""Gemini interpretation layer with actionable diagnostics and deterministic fallback."""
import json
import logging
import os
import re
import time

logger = logging.getLogger("netcoop.gemini")

LIST_FIELDS = {"possible_impacts", "follow_up_checks", "corroborating_evidence",
               "uncertainties", "additional_checks", "operator_cautions"}


def _clean(data, expected_keys):
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    result = {}
    for key in expected_keys:
        value = data.get(key)
        if key in LIST_FIELDS:
            if isinstance(value, str):
                value = [value] if value.strip() else []
            elif not isinstance(value, list):
                value = []
            result[key] = [str(x)[:400] for x in value if x is not None][:10]
        elif key == "summary":
            result[key] = str(value or "")[:1500]
        else:
            result[key] = value
    return result


def _safe_error_details(exc, api_key):
    """Extract useful SDK error details without exposing credentials or request data."""
    code = getattr(exc, "code", None)
    status = getattr(exc, "status", None)
    message = getattr(exc, "message", None) or str(exc) or type(exc).__name__
    message = str(message)[:1200]
    if api_key:
        message = message.replace(api_key, "[REDACTED]")
    message = re.sub(r"(?i)(key|api[_ -]?key)=([^&\\s]+)", r"\\1=[REDACTED]", message)
    return code, status, message


def _is_retryable(code, status, exc):
    # Retry transient rate-limit/server/network errors, not bad requests or credentials.
    if code in (400, 401, 403, 404):
        return False
    if code == 429 or (isinstance(code, int) and code >= 500):
        return True
    name = type(exc).__name__.lower()
    return any(token in name for token in ("timeout", "connection", "server", "resourceexhausted"))


def analyze_with_gemini(agent_name, task, payload, expected_keys):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.warning("Gemini skipped for %s: GEMINI_API_KEY is not configured.", agent_name)
        return {"provider": "gemini", "status": "skipped", "message": "GEMINI_API_KEY is not configured."}
    if not isinstance(payload, dict):
        logger.error("Gemini skipped for %s: payload must be a JSON object.", agent_name)
        return {"provider": "gemini", "status": "error_fallback", "message": "Invalid agent payload; deterministic result retained."}

    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
    except Exception as exc:
        code, status, detail = _safe_error_details(exc, api_key)
        logger.exception("Gemini client initialization failed for %s (%s): %s",
                         agent_name, type(exc).__name__, detail)
        return {"provider": "gemini", "model": model, "status": "error_fallback",
                "error_type": type(exc).__name__, "error_code": code, "error_status": status,
                "error_message": detail, "message": "Gemini client initialization failed; deterministic result retained."}

    prompt = f"""You are {agent_name} in NetCoop AI.
Task: {task}
Use only the supplied telemetry and deterministic findings. Never invent device IDs, metric values, thresholds, topology, or causes.
The raw telemetry is included when available. Do not say telemetry is absent if records are present.
Explicitly distinguish measured facts, missing fields, and hypotheses.
Never override deterministic classification or recommend disruptive changes without operator approval.
Return a JSON object with exactly these keys: {', '.join(expected_keys)}.
Input: {json.dumps(payload, default=str)[:24000]}
"""
    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model, contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            raw_text = response.text or ""
            data = json.loads(raw_text)
            return {"provider": "gemini", "model": model, "status": "completed",
                    "output": _clean(data, expected_keys)}
        except Exception as exc:
            last_error = exc
            code, status, detail = _safe_error_details(exc, api_key)
            retryable = _is_retryable(code, status, exc)
            logger.exception(
                "Gemini request failed: agent=%s model=%s attempt=%s/3 "
                "exception=%s code=%s status=%s retryable=%s detail=%s",
                agent_name, model, attempt + 1, type(exc).__name__, code, status,
                retryable, detail
            )
            if not retryable or attempt == 2:
                break
            time.sleep(0.5 * (2 ** attempt))

    code, status, detail = _safe_error_details(last_error, api_key)
    return {"provider": "gemini", "model": model, "status": "error_fallback",
            "error_type": type(last_error).__name__, "error_code": code,
            "error_status": status, "error_message": detail,
            "message": "Gemini request failed; deterministic result retained."}


def analyze_performance_with_gemini(records, rule_findings, rule_evidence):
    result = analyze_with_gemini("Performance Agent",
        "Interpret latency, jitter, packet loss, throughput, utilization and queue drops.",
        {"telemetry": records[:50], "findings": rule_findings, "evidence": rule_evidence},
        ["summary", "possible_impacts", "follow_up_checks"])
    if result.get("status") == "completed":
        output = result.pop("output")
        result.update(output)
    else:
        result.update({"summary": None, "possible_impacts": [], "follow_up_checks": []})
    return result
