"""Groq interpretation layer with actionable diagnostics and deterministic fallback."""
import json, logging, os, re, time
logger = logging.getLogger("netcoop.groq")
LIST_FIELDS = {"possible_impacts", "follow_up_checks", "corroborating_evidence", "uncertainties", "additional_checks", "operator_cautions"}

def _clean(data, expected_keys):
    if not isinstance(data, dict): raise ValueError("Expected a JSON object")
    result = {}
    for key in expected_keys:
        value = data.get(key)
        if key in LIST_FIELDS:
            if isinstance(value, str): value = [value] if value.strip() else []
            elif not isinstance(value, list): value = []
            result[key] = [str(x)[:400] for x in value if x is not None][:10]
        elif key == "summary": result[key] = str(value or "")[:1500]
        else: result[key] = value
    return result

def _safe_error_details(exc, api_key):
    code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    status = getattr(exc, "status", None)
    message = str(getattr(exc, "message", None) or exc or type(exc).__name__)[:1200]
    if api_key: message = message.replace(api_key, "[REDACTED]")
    message = re.sub(r"(?i)(key|api[_ -]?key)=([^&\s]+)", r"\1=[REDACTED]", message)
    return code, status, message

def _is_retryable(code, exc):
    if code in (400, 401, 403, 404, 422): return False
    if code == 429 or (isinstance(code, int) and code >= 500): return True
    name = type(exc).__name__.lower()
    return any(x in name for x in ("timeout", "connection", "server", "ratelimit"))

def _numeric_tokens(value):
    """Return normalized numeric tokens from text/JSON for evidence comparison."""
    return {token.rstrip("%") for token in re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?%?", str(value))}


def _sanitize_numeric_claims(cleaned, payload):
    """Remove only unsupported numeric sentences/items; preserve grounded prose."""
    source_numbers = _numeric_tokens(json.dumps(payload, default=str))
    removed = 0
    result = dict(cleaned)

    summary = result.get("summary")
    if isinstance(summary, str) and summary.strip():
        # Split conservatively at sentence boundaries. A claim with an ungrounded
        # number is removed, while neighbouring grounded sentences are retained.
        kept_sentences = []
        for sentence in re.split(r"(?<=[.!?])\s+", summary.strip()):
            if _numeric_tokens(sentence) - source_numbers:
                removed += 1
            else:
                kept_sentences.append(sentence)
        result["summary"] = " ".join(kept_sentences)

    for key in LIST_FIELDS:
        value = result.get(key)
        if isinstance(value, list):
            kept_items = []
            for item in value:
                if _numeric_tokens(item) - source_numbers:
                    removed += 1
                else:
                    kept_items.append(item)
            result[key] = kept_items

    if removed and not result.get("summary"):
        result["summary"] = (
            "Some AI statements were omitted because their numeric claims could not "
            "be verified against supplied telemetry. Deterministic findings are retained."
        )
    return result, removed


_METRIC_TERMS = {
    "latency": ("latency_ms",), "delay": ("latency_ms", "jitter_ms"),
    "jitter": ("jitter_ms",), "packet loss": ("packet_loss_pct",),
    "throughput": ("throughput_mbps",), "utilization": ("link_utilization_pct", "utilization_pct"),
    "queue": ("queue_drops",), "interface error": ("interface_errors", "crc_errors", "input_errors", "output_errors"),
    "crc": ("crc_errors",), "link flap": ("link_flaps", "link_flap_count"),
    "wifi": ("signal_strength_dbm", "wifi_signal_dbm", "signal_dbm", "rssi_dbm"),
    "signal strength": ("signal_strength_dbm", "wifi_signal_dbm", "signal_dbm", "rssi_dbm"),
    "retransmission": ("retransmissions", "retry_rate_pct"),
    "dns": ("service", "query_failures", "dns_response_ms", "dns_success_pct", "dns_status", "dns_errors"),
    "dhcp": ("service", "lease_failures", "dhcp_lease_status", "dhcp_errors", "dhcp_success_pct"),
    "cpu": ("cpu_usage_pct",), "memory": ("memory_usage_pct",),
}
_CONNECTIVITY_KEYS = {"service", "query_failures", "lease_failures", "signal_strength_dbm",
                      "retransmissions", "interface_errors", "link_flaps"}

def _payload_keys(value):
    keys = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(str(key).lower())
            keys.update(_payload_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(_payload_keys(item))
    return keys

def _unsupported_metric_reference(text, available):
    lower = str(text).lower().replace("wi-fi", "wifi").replace("wi fi", "wifi")
    # Diagnostic recommendations may legitimately ask the operator to collect
    # currently-missing telemetry; do not treat those as claims about observed health.
    if re.match(r"^\s*(collect|gather|measure|check|monitor|verify|inspect|review|capture|enable)\b", lower):
        return None
    for phrase, aliases in _METRIC_TERMS.items():
        if phrase in lower and not any(alias in available for alias in aliases):
            return phrase
    return None

def _connectivity_claim_without_evidence(text, available):
    lower = str(text).lower().replace("wi-fi", "wifi")
    phrases = (
        "no connectivity issues", "no connectivity problem",
        "connectivity issues detected", "connectivity problem detected",
        "connectivity is healthy", "connectivity healthy",
        "connectivity status is normal", "connectivity is normal",
        "connectivity is stable", "connectivity stable",
        "no connectivity fault", "connectivity working normally",
    )
    return any(p in lower for p in phrases) and not bool(_CONNECTIVITY_KEYS & available)

def _sanitize_evidence_claims(cleaned, payload):
    """Remove claims about metric families/domains absent from supplied telemetry."""
    available = _payload_keys(payload)
    result = dict(cleaned)
    removed = 0
    summary = result.get("summary")
    if isinstance(summary, str) and summary.strip():
        kept = []
        for sentence in re.split(r"(?<=[.!?])\s+", summary.strip()):
            if (_unsupported_metric_reference(sentence, available)
                    or _connectivity_claim_without_evidence(sentence, available)):
                removed += 1
            else:
                kept.append(sentence)
        result["summary"] = " ".join(kept)
    for key in LIST_FIELDS:
        items = result.get(key)
        if isinstance(items, list):
            kept = []
            for item in items:
                if (_unsupported_metric_reference(item, available)
                        or _connectivity_claim_without_evidence(item, available)):
                    removed += 1
                else:
                    kept.append(item)
            result[key] = kept
    if removed and not result.get("summary"):
        result["summary"] = ("AI statements were omitted because they assessed metrics or "
                             "connectivity domains not present in supplied telemetry.")
    return result, removed

def analyze_with_groq(agent_name, task, payload, expected_keys):
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_groq_api_key_here":
        logger.warning("Groq skipped for %s: GROQ_API_KEY is not configured.", agent_name)
        return {"provider": "groq", "status": "skipped", "message": "GROQ_API_KEY is not configured."}
    if not isinstance(payload, dict):
        return {"provider": "groq", "status": "error_fallback", "message": "Invalid agent payload; deterministic result retained."}
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()
    try:
        from groq import Groq
        client = Groq(api_key=api_key, timeout=30.0, max_retries=0)
    except Exception as exc:
        code, status, detail = _safe_error_details(exc, api_key)
        logger.exception("Groq client initialization failed for %s (%s): %s", agent_name, type(exc).__name__, detail)
        return {"provider":"groq", "model":model, "status":"error_fallback", "error_type":type(exc).__name__, "error_code":code, "error_status":status, "error_message":detail, "message":"Groq client initialization failed; deterministic result retained."}
    # Keep prompts compact, especially for the correlation agent where specialist
    # findings/evidence already summarize the raw telemetry.
    payload_text = json.dumps(payload, default=str, separators=(",", ":"))
    payload_limit = int(os.getenv("GROQ_PROMPT_MAX_CHARS", "14000"))
    if len(payload_text) > payload_limit:
        payload_text = payload_text[:payload_limit] + " [INPUT_TRUNCATED]"
    prompt = f"""You are {agent_name} in NetCoop AI.
Task: {task}
Rules:
- Use only the supplied evidence. Never invent device IDs, metric values, thresholds, topology, or causes.
- Treat deterministic classification as authoritative; do not change it.
- Distinguish observed facts, missing fields, and hypotheses.
- Keep every field concise. Summary: at most 2 short sentences. Each list: at most 3 short items.
- If evidence is insufficient, state the uncertainty rather than guessing.
Return one valid JSON object with exactly these keys: {', '.join(expected_keys)}.
Input: {payload_text}"""
    try:
        max_tokens = max(1024, min(8192, int(os.getenv("GROQ_MAX_COMPLETION_TOKENS", "4096"))))
    except ValueError:
        max_tokens = 4096
    last_error = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role":"system","content":"You are a careful network operations analyst. Return valid JSON only."},{"role":"user","content":prompt}],
                response_format={"type":"json_object"}, temperature=0.1, max_completion_tokens=max_tokens)
            data = json.loads(response.choices[0].message.content or "")
            cleaned = _clean(data, expected_keys)
            # Validate each sentence/list item independently. The earlier whole-
            # response check discarded every useful sentence if even one item had
            # an unsupported number (for example a generic numbered recommendation).
            cleaned, removed_claims = _sanitize_numeric_claims(cleaned, payload)
            cleaned, removed_domain = _sanitize_evidence_claims(cleaned, payload)
            removed_claims += removed_domain
            if removed_claims:
                logger.warning(
                    "Removed %s unsupported numeric statement(s) for %s; retained grounded interpretation.",
                    removed_claims, agent_name,
                )
            return {
                "provider": "groq", "model": model, "status": "completed",
                "output": cleaned,
                **({"guard_warnings": [f"{removed_claims} unsupported evidence statement(s) omitted"]} if removed_claims else {}),
            }
        except Exception as exc:
            last_error = exc; code, status, detail = _safe_error_details(exc, api_key)
            retryable = _is_retryable(code, exc)
            error_text = str(getattr(exc, "message", None) or exc).lower()
            token_truncation = ("max completion tokens" in error_text or "max_tokens" in error_text) and ("json_validate_failed" in error_text or "failed to generate json" in error_text)
            if token_truncation:
                logger.error(
                    "Groq JSON output reached completion-token limit for %s (limit=%s). "
                    "Use a shorter agent payload or increase GROQ_MAX_COMPLETION_TOKENS.",
                    agent_name, max_tokens,
                )
            logger.exception("Groq request failed: agent=%s model=%s attempt=%s/3 exception=%s code=%s status=%s retryable=%s detail=%s", agent_name, model, attempt+1, type(exc).__name__, code, status, retryable, detail)
            if not retryable or attempt == 2: break
            time.sleep(0.5 * (2 ** attempt))
    code, status, detail = _safe_error_details(last_error, api_key)
    return {"provider":"groq", "model":model, "status":"error_fallback", "error_type":type(last_error).__name__, "error_code":code, "error_status":status, "error_message":detail, "message":"Groq request failed; deterministic result retained."}

def analyze_performance_with_groq(records, rule_findings, rule_evidence):
    result = analyze_with_groq("Performance Agent", "Interpret latency, jitter, packet loss, throughput, utilization and queue drops.", {"telemetry":records[:50],"findings":rule_findings,"evidence":rule_evidence}, ["summary","possible_impacts","follow_up_checks"])
    if result.get("status") == "completed": result.update(result.pop("output"))
    else: result.update({"summary":None,"possible_impacts":[],"follow_up_checks":[]})
    return result
