# Step 4.6 — Groq Numeric Guard Improvement

## What changed
- Replaced whole-response numeric rejection with sentence-level and list-item-level validation.
- Numeric values already present in telemetry, findings, and thresholds are accepted (including percent values such as `8%` when source evidence contains `8`).
- Only statements containing numeric tokens absent from the supplied payload are omitted.
- Grounded prose and valid recommendations are retained instead of withholding an entire agent interpretation.
- The Groq response includes `guard_warnings` when unsupported numeric statements were omitted.
- Deterministic diagnosis and root-cause classification remain authoritative.

## Tests
Run from `backend`:

```powershell
python -m unittest discover -s tests -v
```

15 tests passed in the build environment. Groq live calls were skipped because no API key was configured in the build environment; verify live model behaviour using your own `.env` key.
