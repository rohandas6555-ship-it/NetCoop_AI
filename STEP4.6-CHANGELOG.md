
## Step 4.7 – Groq correlation JSON/token reliability
- Increased the default Groq completion budget from 1,800 to 4,096 tokens (configurable, capped at 8,192).
- Reduced correlation-agent prompt size by passing specialist findings/evidence and telemetry field names instead of repeating raw telemetry rows.
- Added compact-output instructions and configurable prompt-size protection.
- Added a targeted diagnostic log for JSON responses truncated by the completion-token limit.
- Deterministic classification and fallback behavior remain authoritative.
