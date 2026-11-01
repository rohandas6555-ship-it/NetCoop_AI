# NetCoop AI

**Evidence-first, multi-agent network fault diagnosis**

NetCoop AI analyzes uploaded network telemetry and produces a structured diagnostic report. Its Python backend runs five collaborating specialist agents: three agents inspect separate telemetry domains, a correlation agent combines their findings, and a recommendation agent prepares operator actions. Deterministic rules establish measurable findings and the final root-cause classification; Groq is used for supplementary interpretation and cannot replace the deterministic diagnosis.

> **Project scope:** This version is a synthetic-telemetry demonstration. It does not connect to IIT Bhubaneswar's production network or query live routers, switches, access points, packet captures, network topology, or historical monitoring baselines.

## Live demo

- **Web application:** https://nettcoop-1.onrender.com/
- **Source repository:** https://github.com/narayankr12/NETTCOOP

## What it does

- Accepts CSV and JSON network telemetry files (maximum 10 MB).
- Validates file format and reports telemetry-quality issues such as missing device identifiers, empty cells, invalid numeric values, and unknown columns.
- Runs five specialist agents through a sequential Python orchestrator.
- Correlates evidence from performance, infrastructure, and connectivity telemetry.
- Reports probable root cause, affected devices, evidence, telemetry-domain coverage, heuristic confidence, limitations, and recommended actions.
- Uses Groq for supplementary agent interpretation when configured; deterministic diagnosis remains available when Groq is unavailable.
- Provides account-based report history and exports evidence as CSV or a complete report as JSON. Reports can also be printed or saved as PDF from the browser.
- Includes five synthetic sample scenarios for demonstration.

## How the diagnostic workflow works

```text
CSV / JSON telemetry upload
            |
            v
File validation and record parsing
            |
            v
       Orchestrator
            |
     +------+------+ 
     |      |      |
     v      v      v
Performance Infrastructure Connectivity
  Agent      Agent       Agent
     |      |      |
     +------+------+ 
            |
            v
    Fault Correlation Agent
            |
            v
    Recommendation Agent
            |
            v
     Unified JSON report
            |
            v
 Dashboard, report history and exports
```

The agents are separate functional Python modules coordinated sequentially in one backend process; they are not independently deployed services.

### Agent responsibilities

| Agent | Telemetry it owns | Main responsibility |
|---|---|---|
| **Performance Agent** | `latency_ms`, `jitter_ms`, `packet_loss_pct`, `link_utilization_pct`, `queue_drops` | Detects performance degradation and congestion indicators. The throughput field is included in coverage assessment and LLM context descriptions, but there is no deterministic throughput threshold in the current rule implementation. |
| **Infrastructure Agent** | `device_status` (or eligible generic `status`), `cpu_usage_pct`, `memory_usage_pct`, `interface_errors`, `link_flaps` | Detects device-health and wired-interface issues. |
| **Connectivity Agent** | `service`, DNS query failures, DHCP lease failures, Wi-Fi signal strength and retransmissions | Detects DNS/DHCP service problems and weak wireless connectivity. |
| **Fault Correlation Agent** | Findings and evidence from the three specialist agents, plus telemetry-domain coverage | Applies deterministic cause-priority rules, consolidates evidence, calculates heuristic confidence, and flags incomplete coverage. |
| **Recommendation Agent** | Correlated cause and supporting evidence | Selects predefined corrective actions and requests supplementary Groq review where available. |

## Agent Communication, Message Structure & Orchestration

NetCoop AI uses structured, in-process communication between its five specialized agents. Each agent receives the relevant telemetry data or findings from previous stages and returns a structured Python dictionary containing its results. The orchestrator manages the sequence of execution and passes these findings to the next agent.

### 1. Agent Communication Architecture

The system follows a sequential orchestration model:

1. **Performance Agent:** Analyzes network performance metrics such as latency, jitter, packet loss, link utilization, and queue drops.
2. **Infrastructure Agent:** Examines infrastructure-related metrics, including CPU usage, memory usage, device status, interface errors, and link flaps.
3. **Connectivity Agent:** Checks connectivity indicators such as DNS failures, DHCP lease failures, Wi-Fi signal strength, retransmissions, and service status.
4. **Fault Correlation Agent:** Receives the findings from the three specialist agents, correlates supporting evidence, considers telemetry coverage, and identifies the most likely fault category.
5. **Recommendation Agent:** Uses the correlated diagnosis to select relevant corrective actions and may request additional interpretation from the Groq LLM service.

### 2. Communication Message Structure

Agents communicate through structured Python dictionaries rather than unstructured text or direct user-facing messages.

The communication flow follows this general structure:

| Communication stage | Input | Output |
|---|---|---|
| Telemetry to specialist agents | Validated telemetry records and device information | Agent-specific findings and supporting evidence |
| Specialist agents to correlation agent | Performance, infrastructure, and connectivity findings | Correlated diagnosis, confidence score, and alternative causes |
| Correlation agent to recommendation agent | Suspected root cause and supporting evidence | Recommended corrective actions |
| Orchestrator to API | Results from the diagnostic workflow | Unified JSON diagnostic report |

Each agent's result is collected by the orchestrator and passed to the next stage. This allows the agents to work independently on their specialized diagnostic responsibilities while contributing to one unified diagnosis.

### 3. Orchestration and Evidence Correlation

The orchestrator controls the complete diagnostic workflow. It invokes the specialist agents, collects their findings, and forwards the combined results to the Fault Correlation Agent.

The correlation stage evaluates evidence from multiple telemetry domains instead of relying on a single metric. It uses predefined diagnostic rules and priority-based fault classification to identify a suspected root cause.

The system also considers telemetry coverage. If important telemetry domains are missing, it can return an `insufficient_data` status instead of presenting an unsupported diagnosis.

The confidence value is a heuristic score adjusted according to available telemetry coverage. It is not a calibrated probability of the diagnosis being correct.

### 4. Failure Handling and Missing Agent Results

NetCoop AI includes validation and error-handling mechanisms to make the diagnostic workflow more reliable.

- **Invalid telemetry files:** Unsupported formats, empty files, invalid JSON, missing CSV headers, and oversized uploads are rejected during validation.
- **Incomplete telemetry:** Missing telemetry domains are identified and reflected in the diagnostic result.
- **Invalid telemetry values:** Data-quality checks identify invalid numeric values, empty cells, missing device IDs, and unknown columns.
- **LLM service failure:** If the Groq service is unavailable, its API key is missing, or a request fails, the system retains the deterministic diagnostic results and predefined recommendations.
- **Uncertain diagnosis:** When the available evidence is insufficient, the system reports uncertainty rather than claiming a confirmed root cause.

The deterministic diagnostic workflow remains the primary source of diagnosis. The LLM is used only for supplementary interpretation and does not replace the rule-based fault correlation process.

### 5. Unified Diagnostic Output

After orchestration is complete, the backend returns a unified JSON report containing information such as:

- Incident ID and diagnostic status
- Suspected root cause
- Heuristic confidence score and its explanation
- Affected devices
- Supporting evidence
- Alternative possible causes
- Recommended corrective actions
- Evidence sources
- Telemetry coverage and quality information
- Individual agent results
- Supplementary LLM analysis, when available
- Validation details and diagnostic limitations

This unified output allows the frontend to present the findings in a consistent format, regardless of which agent identified the initial evidence.

**Architecture Note:** The five agents currently operate as Python modules within the same backend application. Their communication is handled through structured dictionaries passed between functions under the control of the orchestrator. They are logically specialized agents, not independently deployed microservices.

### Deterministic checks and default thresholds

Thresholds are centralized in `backend/app/config/thresholds.py` and can be overridden with environment variables.

| Metric | Default rule |
|---|---:|
| Latency | `>= 100 ms` |
| Jitter | `>= 20 ms` |
| Packet loss | `>= 3%` |
| Link utilization | `>= 85%` |
| Queue drops | `> 0` |
| CPU usage | `>= 90%` |
| Memory usage | `>= 90%` |
| Interface error delta | `> 0` |
| Link flap delta | `> 0` |
| Wi-Fi signal strength | `<= -75 dBm` |
| Wi-Fi retransmissions | `>= 20` |
| DNS query failures | `> 10` |
| DHCP lease failures | `> 0` |

**Counter note:** `interface_errors` and `link_flaps` are intended to represent positive counter deltas over the measurement interval, not lifetime cumulative totals. Calculate interval deltas before submitting real counter data.

### Root-cause correlation

The correlation agent uses the following deterministic priority when evidence for multiple categories is present:

1. DNS/DHCP service failure
2. Link congestion
3. Weak Wi-Fi signal
4. Ethernet/interface fault
5. General infrastructure or connectivity degradation when findings exist but do not isolate a specific cause
6. No significant fault detected when no configured thresholds are crossed

When no fault is detected but one or more telemetry domains are missing, the report instead says **“No fault detected in available telemetry; coverage incomplete.”** The application must not interpret missing telemetry as proof that the overall network is healthy.

Telemetry coverage is assessed across three groups: performance, infrastructure, and connectivity. The coverage ratio is the proportion of these groups represented by at least one recognized field; it is not a measure of the percentage of all possible metrics collected.

### Confidence

The report's `confidence` is a **heuristic score**, adjusted using telemetry-domain coverage. It is not a calibrated probability that the root cause is correct. The report labels this explicitly through:

- `confidence_type`: `heuristic_score_not_calibrated_probability`
- `confidence_basis`: a description of the coverage-adjusted heuristic

## Groq integration

Groq is an optional interpretation layer used by the active agent workflow. The deterministic agents establish measurable findings, the correlation agent establishes the root-cause classification, and the recommendation agent supplies predefined actions. Groq may add concise summaries, possible impacts, follow-up checks, uncertainty notes, or cautious supplementary checks.

The integration:

- Requests JSON-formatted responses with agent-specific expected fields.
- Instructs the model to use supplied evidence and not invent device IDs, metric values, thresholds, topology, or causes.
- Filters unsupported numeric claims and claims about telemetry domains not present in the supplied data.
- Retries selected transient failures (up to three attempts).
- Retains deterministic results when the API key is absent or a Groq request fails.

The current active workflow imports `groq_service.py`. A `gemini_service.py` file is also present in the repository, but it is not wired into the active orchestrator/agent execution path.

## Sample scenarios

The frontend bundles these sample files under `frontend/public/samples/`:

| File | Demonstrates | Expected report status / classification |
|---|---|---|
| `normal_network.csv` | Normal-looking telemetry with incomplete domain coverage | `insufficient_data` — no fault detected in available telemetry; coverage incomplete |
| `link_congestion.csv` | High utilization and/or queue drops with performance degradation | `investigate` — Link congestion |
| `weak_wifi_signal.csv` | Weak signal and/or elevated retransmissions | `investigate` — Weak Wi-Fi signal |
| `ethernet_fault.csv` | Interface errors or link flaps | `investigate` — Ethernet/interface fault |
| `dns_dhcp_failure.json` | DNS/DHCP service failure indicators | `investigate` — DNS/DHCP service failure |

The scenario selector is included in the report as a scenario hint; the current deterministic diagnostic rules evaluate the uploaded telemetry rather than using the selected scenario to force a diagnosis.

## Technology stack

### Backend

- Python
- FastAPI
- Uvicorn
- Groq Python SDK (optional LLM interpretation)
- SQLite (user accounts and diagnostic report history)
- Pydantic / FastAPI request validation
- `python-multipart` for file uploads
- `python-dotenv` for environment configuration

### Frontend

- React
- Vite
- JavaScript (ES modules)
- `lucide-react` icons
- CSS

## Repository structure

```text
NETTCOOP/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── performance_agent.py
│   │   │   ├── infrastructure_agent.py
│   │   │   ├── connectivity_agent.py
│   │   │   ├── correlation_agent.py
│   │   │   └── recommendation_agent.py
│   │   ├── api/routes/
│   │   │   ├── auth_routes.py
│   │   │   ├── upload_routes.py
│   │   │   └── diagnosis_routes.py
│   │   ├── config/thresholds.py
│   │   ├── llm/
│   │   │   ├── groq_service.py
│   │   │   └── gemini_service.py
│   │   ├── orchestration/diagnosis_orchestrator.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── file_validation_service.py
│   │   │   ├── telemetry_quality_service.py
│   │   │   └── report_history_service.py
│   │   └── main.py
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   ├── samples/
│   │   └── netcoop-mark.svg
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── styles.css
├── DEMO-VALIDATION.md
├── HACKATHON_DEMO_GUIDE.md
└── README.md
```

## Getting started locally

### Prerequisites

- Python 3.10+ (use a version supported by the installed FastAPI and dependencies)
- Node.js and npm
- A Groq API key is optional; without it, deterministic diagnosis still runs and LLM interpretation is skipped.

### 1. Clone the repository

```bash
git clone https://github.com/narayankr12/NETTCOOP.git
cd NETTCOOP
```

### 2. Configure and start the backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file from the example:

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Edit `backend/.env` and set at least a strong, unique `NETCOOP_AUTH_SECRET`. To enable Groq interpretation, also set `GROQ_API_KEY`. The default model is configured by `GROQ_MODEL` in `.env.example`.

Start the API from the `backend/` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

The API health endpoint is available at `http://localhost:8000/health`. FastAPI's interactive API documentation is available at `http://localhost:8000/docs`.

### 3. Configure and start the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

The frontend defaults to `http://localhost:8000/api` for the backend. If your backend runs elsewhere, create `frontend/.env` and set:

```env
VITE_API_URL=https://your-backend-host.example/api
```

Start the Vite development server:

```bash
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`). The backend CORS configuration allows localhost on port 5173 and the optional origin configured by `FRONTEND_ORIGIN`.

## API endpoints

All application routes below are mounted under `/api`, except the health check.

| Method | Endpoint | Authentication | Purpose |
|---|---|---|---|
| `GET` | `/health` | No | Backend health check |
| `POST` | `/api/auth/register` | No | Register a user and return a bearer token |
| `POST` | `/api/auth/login` | No | Authenticate and return a bearer token |
| `GET` | `/api/auth/me` | Bearer token | Return the authenticated user |
| `POST` | `/api/upload/validate` | Bearer token | Validate an uploaded CSV/JSON file and return file metadata |
| `POST` | `/api/diagnosis/start` | Bearer token | Upload telemetry, run all agents and return/save a diagnostic report |
| `GET` | `/api/reports` | Bearer token | List the authenticated user's saved reports |
| `GET` | `/api/reports/{incident_id}` | Bearer token | Retrieve one saved report belonging to the authenticated user |

### Starting a diagnosis

`POST /api/diagnosis/start` accepts multipart form data:

- `file`: telemetry file (`.csv` or `.json`)
- `scenario`: optional scenario label; defaults to `Auto-detect from file`

Include the bearer token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

The endpoint returns a JSON report containing fields such as:

- `incident_id`, `status`, `suspected_root_cause`
- `confidence`, `confidence_type`, `confidence_basis`
- `affected_devices`, `supporting_evidence`, `alternative_causes`
- `recommended_actions`, `evidence_sources`
- `telemetry_coverage`, `telemetry_quality`, `schema_diagnostics`
- `agent_results`, `llm_analysis`, `validation`, `orchestration`, `limitations`

## Authentication and data storage

- User registration and login are handled by the FastAPI authentication routes.
- Passwords are stored as PBKDF2-HMAC-SHA256 password hashes, not plaintext passwords.
- Authenticated API requests use signed bearer tokens with a 12-hour expiry.
- SQLite stores user accounts and report history. Reports are scoped to the authenticated user.
- The SQLite database is created by the application services when required.

For a production deployment, configure a strong secret using `NETCOOP_AUTH_SECRET`, use HTTPS, restrict CORS to trusted frontend origins, and use persistent storage for the SQLite database. Do not commit `.env` or expose API keys.

## Configuration reference

| Environment variable | Default / purpose |
|---|---|
| `GROQ_API_KEY` | Optional Groq API key; without it, LLM interpretation is skipped |
| `GROQ_MODEL` | `openai/gpt-oss-20b` in the supplied example |
| `GROQ_MAX_COMPLETION_TOKENS` | `4096` in the supplied example |
| `GROQ_PROMPT_MAX_CHARS` | `14000` in the supplied example |
| `NETCOOP_AUTH_SECRET` | **Set a strong unique secret; do not use the development fallback in production** |
| `FRONTEND_ORIGIN` | Additional allowed frontend origin for backend CORS |
| `NETCOOP_LATENCY_MS` | `100` |
| `NETCOOP_JITTER_MS` | `20` |
| `NETCOOP_PACKET_LOSS_PCT` | `3` |
| `NETCOOP_LINK_UTILIZATION_PCT` | `85` |
| `NETCOOP_QUEUE_DROPS` | `0` |
| `NETCOOP_CPU_USAGE_PCT` | `90` |
| `NETCOOP_MEMORY_USAGE_PCT` | `90` |
| `NETCOOP_INTERFACE_ERRORS_DELTA` | `0` |
| `NETCOOP_LINK_FLAPS_DELTA` | `0` |
| `NETCOOP_WIFI_SIGNAL_DBM` | `-75` |
| `NETCOOP_WIFI_RETRANSMISSIONS` | `20` |
| `NETCOOP_DNS_QUERY_FAILURES` | `10` |
| `NETCOOP_DHCP_LEASE_FAILURES` | `0` |

See `backend/.env.example` for the complete example configuration.

## Tests and validation

Run the backend regression tests from the `backend/` directory:

```bash
python -m unittest discover -s tests -v
```

The tests cover agent domain isolation, missing-domain wording, Groq numeric/evidence/domain guards, reliability thresholds, and end-to-end agent behavior.

The repository's `DEMO-VALIDATION.md` records a validation run dated **2026-10-31**: 12 automated tests passed, and the five bundled synthetic sample scenarios returned the expected diagnostic outcomes through the FastAPI test client. That validation notes that Groq was not configured in that environment, so live Groq responses were not tested there. It also notes that the frontend production build was not verified in that environment.

To build the frontend locally:

```bash
cd frontend
npm install
npm run build
```

## Limitations and future work

Current limitations:

- Uses synthetic or user-supplied telemetry rather than live campus monitoring integrations.
- Does not discover network topology or inspect packet captures.
- Does not compare telemetry against historical baselines.
- Uses a deterministic priority order for selecting one primary root-cause classification; simultaneous faults may need richer multi-cause correlation.
- Confidence is heuristic and not calibrated against a labelled incident dataset.
- Agent communication is implemented as in-process structured Python results, not a separately versioned network protocol or independently deployed agent services.
- The frontend's Data Sources and Infrastructure navigation views are informational/empty states; telemetry is supplied through the diagnostic upload workflow.

Potential next steps include authenticated telemetry collectors, vendor-schema adapters, time-window-aware counter normalization, topology-aware correlation, multi-cause ranking, calibrated confidence evaluation, and a formal versioned agent message schema.

## Hackathon context

NetCoop AI was developed for a 24-hour hackathon challenge focused on multi-agent network fault diagnosis and interoperability. The central idea is to combine specialized analysis, structured findings, evidence correlation, explicit uncertainty, and practical operator recommendations in one diagnostic workflow.

---

**NetCoop AI — Network Operations Intelligence**
