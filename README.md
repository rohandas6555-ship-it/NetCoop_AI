# NetCoop AI

**Multi-Agent Network Fault Diagnosis and Interoperability**

NetCoop AI is a web-based, evidence-first network diagnostics prototype. It accepts network telemetry in CSV or JSON format, validates the input, coordinates five specialized analysis agents, and produces a unified diagnostic report with supporting evidence, uncertainty, and recommended actions.

> **Demo scope:** This project demonstrates the workflow using synthetic or authorized test telemetry. It does not currently connect to or monitor the production IIT Bhubaneswar campus network, live network devices, packet captures, or a live topology map.

## Table of contents

- [Problem](#problem)
- [Key features](#key-features)
- [Architecture](#architecture)
- [Agent responsibilities](#agent-responsibilities)
- [Workflow](#workflow)
- [Technology stack](#technology-stack)
- [Repository structure](#repository-structure)
- [Getting started](#getting-started)
- [Environment configuration](#environment-configuration)
- [Sample scenarios](#sample-scenarios)
- [API overview](#api-overview)
- [Testing](#testing)
- [Report and confidence](#report-and-confidence)
- [Security notes](#security-notes)
- [Limitations and future scope](#limitations-and-future-scope)

## Problem

Network faults can arise from high latency, jitter, packet loss, congestion, device resource pressure, interface errors, weak wireless signals, or DNS/DHCP failures. Diagnostic evidence is often spread across different devices and telemetry sources, and the data may be incomplete or inconsistent.

NetCoop AI addresses this challenge by separating analysis into specialist agents, passing structured findings between them, and consolidating the available evidence into one explainable report. The system is designed to report insufficient evidence rather than claim an exact cause when telemetry coverage is incomplete.

## Key features

- CSV and JSON telemetry upload.
- File/schema validation and telemetry quality diagnostics.
- Five specialized agents coordinated by a central orchestrator.
- Deterministic, threshold-based checks for measurable findings.
- Optional Groq-powered supplementary interpretation.
- Evidence grounding and safeguards against unsupported AI claims.
- Telemetry-domain coverage and explicit missing-data reporting.
- Unified incident report with probable cause, evidence, uncertainty, confidence score, and recommended actions.
- User registration/login and per-user incident history.
- Report export as JSON, supporting-evidence CSV, and browser-generated PDF.
- Synthetic sample scenarios for repeatable demonstrations.

## Architecture

```text
                  CSV / JSON telemetry
                           |
                           v
               Validation & normalization
                           |
                           v
                 Diagnosis orchestrator
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
   Performance Agent  Infrastructure   Connectivity
                           Agent           Agent
          |                |                |
          +----------------+----------------+
                           |
                           v
                 Fault Correlation Agent
                           |
                           v
                 Recommendation Agent
                           |
                           v
                Unified diagnostic report
                           |
             Dashboard / JSON / CSV / PDF
```

The agents are Python modules coordinated by a custom orchestrator. They are not separate autonomous processes. Structured Python dictionaries/JSON-compatible objects carry telemetry, findings, evidence, and agent results between stages.

## Agent responsibilities

| Agent | Responsibility | Example telemetry |
|---|---|---|
| Performance Agent | Checks network performance and congestion indicators | latency, jitter, packet loss, throughput, link utilization, queue drops |
| Infrastructure Agent | Checks device and wired infrastructure health | device status, CPU, memory, interface errors, link flaps |
| Connectivity Agent | Checks service and wireless connectivity indicators | DNS query failures, DHCP lease failures, Wi-Fi signal, retransmissions |
| Fault Correlation Agent | Combines specialist findings, assesses coverage, and selects a supported probable cause | findings, evidence, domain coverage, uncertainty |
| Recommendation Agent | Produces practical next steps based on the correlated result | probable cause, evidence, missing telemetry, operator cautions |

Each specialist agent is restricted to its relevant telemetry domain. For example, wired interface errors belong to Infrastructure, while DNS/DHCP and Wi-Fi indicators belong to Connectivity.

## Workflow

1. The user signs in and uploads a CSV or JSON telemetry file.
2. The backend validates the file and parses/normalizes available telemetry.
3. The orchestrator invokes the Performance, Infrastructure, and Connectivity agents.
4. Each specialist performs deterministic checks and may request supplementary Groq interpretation when relevant telemetry is available.
5. The Fault Correlation Agent receives structured findings and evidence, evaluates telemetry coverage, and produces a supported diagnosis or an insufficient-data result.
6. The Recommendation Agent prepares corrective actions and additional checks.
7. The backend returns a unified report; the dashboard displays the result and allows export/history access.

## Technology stack

- **Frontend:** React, Vite, JavaScript, CSS, Lucide icons.
- **Backend:** Python, FastAPI, Uvicorn.
- **Data processing:** Pandas, CSV/JSON parsing and validation.
- **AI interpretation:** Groq API (optional; configured model defaults to `openai/gpt-oss-20b`).
- **Persistence:** SQLite for user accounts and incident history.
- **Authentication:** PBKDF2-HMAC-SHA256 password hashing and signed bearer tokens.

## Repository structure

```text
NetCoop-AI-Step4/
├── backend/
│   ├── app/
│   │   ├── agents/           # Five specialist agents
│   │   ├── api/routes/       # Authentication, upload, diagnosis APIs
│   │   ├── config/           # Deterministic thresholds
│   │   ├── llm/              # Groq integration and output guards
│   │   ├── orchestration/    # Multi-agent coordination
│   │   └── services/         # Auth, validation, report history
│   ├── tests/                # Backend regression tests
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── public/samples/       # Synthetic CSV/JSON scenarios
│   ├── public/               # Branding assets
│   └── src/                  # React dashboard
├── HACKATHON_DEMO_GUIDE.md
└── README.md
```

## Getting started

### Prerequisites

- Python 3.10 or later recommended.
- Node.js and npm.
- A Groq API key only if you want supplementary LLM interpretation. Deterministic diagnosis can run without it.

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd NetCoop-AI-Step4
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the URL of your repository.

### 2. Configure and run the backend

**Windows PowerShell:**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `backend/.env` and configure the values described in [Environment configuration](#environment-configuration). Then start the API:

```powershell
uvicorn app.main:app --reload --port 8000
```

The API health endpoint is available at `http://localhost:8000/health`. FastAPI's interactive API documentation is normally available at `http://localhost:8000/docs`.

**macOS/Linux:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3. Run the frontend

Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`). Keep the backend and frontend running while using the local application.

## Environment configuration

The backend reads its configuration from `backend/.env`. Start with `.env.example` and set a real Groq key only in your local/deployment environment.

| Variable | Purpose | Example/default |
|---|---|---|
| `GROQ_API_KEY` | Enables supplementary Groq interpretation | Keep secret; optional |
| `GROQ_MODEL` | Groq model name | `openai/gpt-oss-20b` |
| `GROQ_MAX_COMPLETION_TOKENS` | Maximum model completion tokens | `4096` |
| `GROQ_PROMPT_MAX_CHARS` | Prompt size guard | `14000` |
| `NETCOOP_AUTH_SECRET` | Signs authentication tokens | Set a long random secret |
| `NETCOOP_LATENCY_MS` | Latency threshold in milliseconds | `100` |
| `NETCOOP_JITTER_MS` | Jitter threshold in milliseconds | `20` |
| `NETCOOP_PACKET_LOSS_PCT` | Packet-loss threshold | `3` |
| `NETCOOP_LINK_UTILIZATION_PCT` | Link-utilization threshold | `85` |
| `NETCOOP_QUEUE_DROPS` | Queue-drop threshold | `0` |
| `NETCOOP_CPU_USAGE_PCT` | CPU utilization threshold | `90` |
| `NETCOOP_MEMORY_USAGE_PCT` | Memory utilization threshold | `90` |
| `NETCOOP_INTERFACE_ERRORS_DELTA` | Interface-error counter delta threshold | `0` |
| `NETCOOP_LINK_FLAPS_DELTA` | Link-flap counter delta threshold | `0` |
| `NETCOOP_WIFI_SIGNAL_DBM` | Weak Wi-Fi signal threshold | `-75` |
| `NETCOOP_WIFI_RETRANSMISSIONS` | Wi-Fi retransmission threshold | `20` |
| `NETCOOP_DNS_QUERY_FAILURES` | DNS query-failure threshold | `10` |
| `NETCOOP_DHCP_LEASE_FAILURES` | DHCP lease-failure threshold | `0` |

Thresholds must be interpreted in the units and collection window used by the telemetry source. Interface-error and link-flap values are treated as interval deltas; cumulative counters should be converted to deltas before upload.

## Sample scenarios

The frontend includes sample telemetry files under `frontend/public/samples/`.

| File | Scenario | Expected demonstration |
|---|---|---|
| `normal_network.csv` | Normal operation with incomplete domain coverage | No threshold breach in available data; report should disclose missing telemetry rather than claim complete network health |
| `link_congestion.csv` | Link congestion | High utilization / congestion-related evidence |
| `weak_wifi_signal.csv` | Weak Wi-Fi signal | Poor signal and/or retransmission evidence |
| `ethernet_fault.csv` | Ethernet/interface fault | Interface error or link-instability evidence |
| `dns_dhcp_failure.json` | DNS/DHCP service failure | Service-specific connectivity failure |

Run the scenarios one at a time and inspect the report, agent results, telemetry coverage, and recommendations. Exact results depend on the sample contents and configured thresholds.

## API overview

The backend exposes the following routes (the exact request/response schemas are available in the FastAPI docs):

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/health` | Backend health check |
| `POST` | `/api/auth/register` | Register a user |
| `POST` | `/api/auth/login` | Authenticate and obtain a bearer token |
| `GET` | `/api/auth/me` | Get the current authenticated user |
| `POST` | `/api/upload/validate` | Validate uploaded telemetry |
| `POST` | `/api/diagnosis/start` | Run the multi-agent diagnosis |
| `GET` | `/api/reports` | List the authenticated user's report history |
| `GET` | `/api/reports/{incident_id}` | Retrieve a prior report |

Authenticated routes require the bearer token returned by login. Use `/docs` to inspect the live API schema.

## Testing

From the `backend` directory, activate the virtual environment and run:

```bash
python -m unittest discover -s tests -v
```

The backend regression suite was recorded as passing **27 tests** in the development environment. Re-run the suite on your own checkout before submission. The tests do not require a live campus network; Groq calls may be skipped when no API key is configured.

For the frontend production build, from `frontend/` run:

```bash
npm run build
```

## Report and confidence

A diagnostic report includes an incident ID, overall status, suspected root cause, heuristic confidence, affected devices where identifiable, supporting evidence, alternative explanations, recommended actions, evidence sources, telemetry coverage, schema diagnostics, agent results, LLM statuses, validation results, and orchestration details.

**Confidence is a heuristic score, not a calibrated probability.** It is adjusted for telemetry-domain coverage and should not be interpreted as a statistical probability that the root cause is correct.

The report's rule-based classification and evidence are authoritative for measurable findings. Groq output is supplementary interpretation; it must not replace deterministic root-cause classification or introduce unsupported evidence. A `skipped` LLM status means the agent did not call Groq (for example, because its telemetry domain was absent). A `partial` overall LLM status can therefore be expected when some agents correctly skip interpretation.

The PDF export uses the browser's native **Print / Save PDF** flow. Choose **Save as PDF** in the browser print dialog. JSON exports the complete report payload; CSV exports supporting evidence rows.

## Security notes

- Never commit `.env`, API keys, database files containing real user information, or production secrets.
- Set a unique, long, random `NETCOOP_AUTH_SECRET` for deployment.
- Use HTTPS for public deployments.
- The included authentication is a hackathon/demo starter, not a fully hardened production identity system. Production use should add rate limiting, secure HttpOnly cookies, account lockout, password reset, email verification, stronger operational monitoring, and appropriate data-retention controls.
- Do not upload confidential or production network telemetry unless you have authorization and have reviewed the deployment's security and data-handling requirements.

## Limitations and future scope

Current scope and known limitations:

- Demonstration uses synthetic or authorized test telemetry; no live campus devices are queried.
- No packet capture, live topology discovery, or historical baseline service is integrated.
- The five agents are modules in one Python application coordinated by an orchestrator, not independently deployed autonomous services.
- Confidence is heuristic and has not been calibrated against a labeled production dataset.
- Automated remediation is not implemented; recommendations are for operator review.
- Authentication needs additional hardening before production use.

Possible future work includes authorized live telemetry connectors, topology-aware correlation, historical baselines, calibrated confidence, richer interoperability/schema-version tests, and human-approved remediation workflows.

---

**Project:** NetCoop AI  
**Focus:** Multi-agent network fault diagnosis, interoperability, and evidence-based reporting.
