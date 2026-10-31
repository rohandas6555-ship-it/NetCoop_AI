# NetCoop AI - Final Demo Validation

Validation performed on 2026-10-31 using the bundled synthetic sample files.

## Backend automated tests

Command:

```bash
python -m unittest discover -s tests -v
```

Result: **12 tests passed**.

## API smoke / end-to-end upload checks

The FastAPI test client was used to call `GET /health` and upload every bundled sample to `POST /api/diagnosis/start`.

| Sample | HTTP | Expected diagnosis | Result |
|---|---:|---|---|
| `normal_network.csv` | 200 | Incomplete telemetry; no confirmed fault | `insufficient_data` |
| `link_congestion.csv` | 200 | Link congestion | `investigate` |
| `ethernet_fault.csv` | 200 | Ethernet/interface fault | `investigate` |
| `weak_wifi_signal.csv` | 200 | Weak Wi-Fi signal | `investigate` |
| `dns_dhcp_failure.json` | 200 | DNS/DHCP service failure | `investigate` |

Health endpoint: HTTP 200, `{"status":"ok","service":"netcoop-api"}`.
All five sample uploads returned five agent results.

## Groq / frontend limitations

- No `GROQ_API_KEY` was configured in this validation environment. Groq calls were skipped and deterministic fallback/classification was exercised. Live Groq API response and quota behaviour remain to be checked with the user's own API key.
- Frontend production build was not verified: Vite was not installed, and dependency installation did not complete in the validation environment. Run `npm install` then `npm run build` in `frontend/` on the demo machine.
- These are synthetic sample-data checks, not validation against real campus devices or real incidents.

## Recommended final rehearsal

1. Configure `GROQ_API_KEY` and `GROQ_MODEL` in backend `.env`.
2. Start backend and confirm `http://localhost:8000/health`.
3. In `frontend/`, run `npm install` and `npm run build`.
4. Start Vite and upload all five bundled sample files through the UI.
5. Confirm the dashboard shows root cause, evidence, affected devices, coverage, recommendations and Groq status.
