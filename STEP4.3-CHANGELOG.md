# NetCoop AI — Step 4.3

## Changes
- Fault Correlation Agent now receives raw telemetry records, record count, coverage details, specialist statuses, deterministic findings and evidence.
- Added telemetry-domain coverage for performance, infrastructure and connectivity.
- Missing telemetry domains lower the heuristic confidence score.
- If no anomaly is detected but one or more domains are missing, report status becomes `insufficient_data`, not `normal`.
- Correlation output explicitly explains that available metrics show no fault but coverage is incomplete.
- Recommendation Agent asks operators to collect missing domains before declaring network health.
- Infrastructure and Connectivity Agents now receive raw telemetry and distinguish `insufficient_data` from `clear`.
- Groq output arrays are normalized safely; Groq retries up to three times and deterministic results remain available on failure.
- Agent failures are isolated so remaining specialists can continue.
- Dashboard shows telemetry coverage and missing diagnostic domains.

## Coverage domains
- Performance: latency, jitter, packet loss, throughput, link utilization, queue drops.
- Infrastructure: status, CPU, memory, interface errors, link flaps.
- Connectivity: DNS/DHCP, Wi-Fi signal, retransmissions.

## Test scope
Run all five bundled synthetic samples. For `normal_network.csv`, expected result is `insufficient_data` because connectivity-domain telemetry is absent; it must not claim full network health. Fault scenarios should continue to report their deterministic root-cause category.
Live Groq API calls must be tested locally with a valid API key. No live campus network was accessed.


## Groq model configuration
- Set the default model to `openai/gpt-oss-20b`, a model listed in Groq's current supported-model documentation.
- Uses Groq Chat Completions with JSON-object response mode.
- Existing local `.env` files must be updated manually with `GROQ_API_KEY` and `GROQ_MODEL=openai/gpt-oss-20b`.


## Groq provider migration
- Replaced Gemini SDK calls with the official Groq Python SDK and Chat Completions API.
- Default model: `openai/gpt-oss-20b`; override with `GROQ_MODEL` after checking Groq active models.
- Uses JSON-object response mode, bounded retries for transient failures, sanitized diagnostics, and deterministic fallback.
- Configure `GROQ_API_KEY` in `backend/.env`; never commit or share the key.
