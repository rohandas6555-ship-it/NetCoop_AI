# Backend — NetCoop AI Step 4.3 (Groq)

Install dependencies from `requirements.txt`, configure `GROQ_API_KEY` in `.env`, then run:

```powershell
uvicorn app.main:app --reload --port 8000
```

`POST /api/diagnosis/start` runs five agents. Groq supplies supplementary interpretation; deterministic telemetry checks and recommendations remain available if the LLM is unavailable. The final JSON contains `agent_results`, `validation`, and `orchestration`.

## Groq configuration

1. Copy `.env.example` to `.env`.
2. Set `GROQ_API_KEY` to an API key created in your GroqCloud console.
3. The default model is `openai/gpt-oss-20b`. You can change it with `GROQ_MODEL` to another active model supported by your Groq account.
4. Install the SDK with `python -m pip install -r requirements.txt`.
5. Restart the backend after changing `.env`.

The integration uses Groq's Chat Completions API with JSON-object response mode. The service makes up to three attempts for transient rate-limit, server, and network failures; it does not retry authentication, permission, missing-model, or invalid-request errors. API keys are redacted from diagnostic messages. Never commit or share `.env`.

## Troubleshooting

After a diagnosis, inspect the backend terminal for `Groq request failed`. The report's `llm_analysis` objects may include `error_code`, `error_status`, and `error_message`. A `skipped` status means `GROQ_API_KEY` is not configured; `error_fallback` means the deterministic pipeline continued after a Groq error.

Groq may make five model calls per diagnosis. Monitor your Groq account's rate limits and usage. No live campus network is accessed; this remains a synthetic telemetry demonstration.

## Configurable diagnosis thresholds (Step 4.5)
Deterministic thresholds are centralized in `app/config/thresholds.py` and can be overridden through environment variables listed in `.env.example`. Interface error and link-flap values are interpreted as counter deltas over the collection interval, not lifetime totals. For real telemetry, calculate interval deltas before submitting records; otherwise a cumulative counter can repeatedly trigger a fault.

Run all deterministic regression tests from this directory:
```bash
python -m unittest discover -s tests -v
```
The suite does not require a Groq API key; Groq calls are skipped when the key is absent.
