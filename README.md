# NetCoop AI — Step 4: Full Multi-Agent Collaboration

Step 4 extends the previous project with Groq-assisted reasoning in all five agents, structured evidence hand-offs, and final report consistency checks.

## What changed
- Performance, Infrastructure and Connectivity agents each run deterministic checks and request supplementary Groq interpretation.
- Fault Correlation Agent receives structured findings/evidence from all three specialist agents, computes the deterministic cause and heuristic confidence, then asks Groq to explain corroboration and uncertainty.
- Recommendation Agent receives the correlated cause and evidence, prepares rule-based actions and asks Groq for additional checks/cautions.
- Groq output never overwrites deterministic root-cause classification or evidence.
- Final report includes per-agent LLM status, evidence/device consistency checks, agent trace and five agent result objects.
- Missing/invalid API key or Groq errors do not stop the diagnosis pipeline.

## Run (Windows PowerShell)
Backend terminal:
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
# Add your key in backend/.env
uvicorn app.main:app --reload --port 8000
```
Frontend terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## Verify
Run all five sample files. In the report inspect `agent_results` (five entries), each `llm_analysis.status`, `validation.llm_agent_statuses`, `validation.affected_devices_match_evidence`, and `orchestration.collaboration`.

Groq may make five model calls per diagnosis. Keep the API key private and monitor quota/cost. `skipped` means no key configured; `error_fallback` means the deterministic pipeline continued after an LLM error.

## Important limits
This is a synthetic-data demonstration, not live campus-network access. The agents are Python modules coordinated by a custom orchestrator, not separate autonomous processes. Confidence remains heuristic and requires calibration against a labeled test set before being described as probability.


## NetCoop AI UI + Authentication update

- A branded responsive operations console and NetCoop AI SVG mark are included.
- Users can register and sign in; passwords are PBKDF2-HMAC-SHA256 hashed in a local SQLite database.
- Login issues a signed 12-hour bearer token. Diagnosis and upload-validation endpoints require that token.
- The frontend stores the session token in browser localStorage and provides logout.
- Configure `NETCOOP_AUTH_SECRET` to a long random secret in `backend/.env` before deployment. Do not expose the development fallback secret publicly.
- The user database is created automatically at `backend/netcoop_users.db`.
- This is a starter authentication layer for a local/demo deployment. For production internet exposure, add HTTPS, rate limiting, email verification, password reset, secure HttpOnly cookies, and account lockout.


## Hackathon showcase upgrades
- Connectivity Agent receives only DNS/DHCP/Wi-Fi fields; wired interface errors and link flaps remain owned by Infrastructure Agent.
- If connectivity fields are absent or empty, the Connectivity Agent marks its domain insufficient and skips Groq rather than inventing a health assessment.
- Each user's diagnosis reports are persisted in the local SQLite database and isolated by authenticated user ID.
- Reports page shows incident history; prior reports can be reopened.
- Diagnostic report supports evidence CSV and full JSON export.
- Evidence-first trust strip explains deterministic findings vs supplementary LLM interpretation.


## Final agent-isolation and reporting polish
- Infrastructure Agent now receives only device status, CPU, memory, interface errors and link flaps. It skips Groq if these fields are absent.
- Shared `status` values on DNS/DHCP service rows are not misclassified as device infrastructure status.
- Telemetry coverage ignores empty/null values and distinguishes DNS/DHCP service status from infrastructure device status.
- Fault Correlation Agent now names available and missing domains explicitly; when there are no findings and coverage is incomplete, its displayed AI summary is replaced with the deterministic coverage explanation.
- Report UI displays deterministic rule status separately from Groq interpretation status and shows completed/skipped/fallback counts.


## PDF and final report delivery
- Diagnostic report includes a branded print stylesheet with A4 page setup.
- Use the `Print / Save PDF` action on a report, then select **Save as PDF** in the browser print dialog.
- JSON export preserves the complete report payload.
- CSV export provides supporting evidence rows for spreadsheet analysis.
- The PDF route uses the browser's native print-to-PDF engine; it does not require an additional PDF package or backend service.
