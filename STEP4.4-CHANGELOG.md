# Step 4.4 – Reliability and telemetry quality

- Added a telemetry quality service that reports unknown columns, missing device identifiers, invalid numeric values, and empty cells.
- Added `telemetry_quality` to every diagnosis report for API consumers and the dashboard.
- Dashboard now displays all telemetry quality warnings rather than only unknown columns and missing device IDs.
- Added a Groq output guard: if the model introduces numeric claims not present in its input payload, its narrative is withheld and deterministic findings remain authoritative.
- Guarded Groq responses are reported separately (`status: guarded`) and counted as processed, not as ordinary unguarded completions.
- Existing deterministic root-cause rules are unchanged.

## Validation

Run `python -m unittest discover -s tests -v` from the backend directory. The test suite validates deterministic scenarios and telemetry-quality diagnostics without requiring a Groq API key.
