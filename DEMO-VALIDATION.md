# NetCoop AI — Demo Validation Report

**Project:** NetCoop AI  
**Category:** Agentic AI — Computer Networks  
**Validation date:** 1 November 2026

## 1. Validation Overview

This document records the available automated testing and demonstration checks for NetCoop AI.

The validation focuses on:
- Backend automated tests.
- Multi-agent execution.
- Telemetry upload and validation.
- Synthetic network fault scenarios.
- Missing telemetry handling.
- Diagnostic report generation.
- AI interpretation safeguards.

## 2. Backend Automated Tests

Command:

```bash
python -m unittest discover -s tests -v
```

**Latest recorded result: 27/27 tests passed.**

The tests cover:
- Reliability thresholds.
- Groq domain isolation.
- Groq numeric evidence safeguards.
- Connectivity domain isolation.
- Infrastructure domain isolation.
- Missing telemetry coverage wording.
- Diagnostic reliability and validation.

## 3. Synthetic Test Scenarios

The application includes the following synthetic telemetry samples:

| Sample | Expected classification |
|---|---|
| `normal_network.csv` | insufficient_data when connectivity telemetry is missing |
| `link_congestion.csv` | investigate — Link congestion |
| `weak_wifi_signal.csv` | investigate — Weak Wi-Fi signal |
| `ethernet_fault.csv` | investigate — Ethernet/interface fault |
| `dns_dhcp_failure.json` | investigate — DNS/DHCP service failure |

These files are intended to demonstrate normal operation and different network fault conditions.

## 4. Deployed Application Upload Check

### Test: normal_network.csv

**Observed result:**
- File uploaded successfully.
- Two telemetry records analyzed.
- Overall status: `insufficient_data`.
- Probable root cause: No fault detected in available telemetry; coverage incomplete.
- Telemetry coverage: 67%.
- Available domains: Performance and Infrastructure.
- Missing domain: Connectivity.
- Five agents executed.
- Four Groq interpretations completed.
- Connectivity Agent AI interpretation skipped.

**Result: PASS**

The application correctly avoided declaring the entire network healthy because connectivity telemetry was missing.

## 5. Agent Execution Validation

| Agent | Responsibility | Expected behaviour |
|---|---|---|
| Performance Agent | Performance metrics | Analyze performance telemetry |
| Infrastructure Agent | Infrastructure metrics | Analyze infrastructure telemetry |
| Connectivity Agent | Connectivity metrics | Skip AI interpretation when connectivity data is absent |
| Fault Correlation Agent | Evidence correlation | Combine findings and identify missing domains |
| Recommendation Agent | Corrective actions | Generate recommendations from the diagnosis |

## 6. AI Reliability and Evidence Safeguards

The system follows an evidence-first approach.

- Deterministic rules establish measurable findings.
- Groq provides supplementary interpretation.
- Unsupported AI statements are filtered.
- Agent-specific telemetry boundaries prevent unrelated metrics from influencing analysis.
- Missing telemetry is reported explicitly.
- Confidence is a heuristic score, not a calibrated probability.

## 7. Report Validation

The diagnostic report supports:

| Output | Purpose |
|---|---|
| JSON | Complete structured diagnostic report |
| CSV | Supporting evidence export |
| PDF | Human-readable printable diagnostic report |

The report includes incident information, probable root cause, confidence, evidence, telemetry coverage, agent results, and recommended actions.

## 8. Frontend Build Status

The frontend production build has not yet been independently verified in the recorded validation environment.

Run the following commands from the `frontend/` directory:

```bash
npm install
npm run build
```

A successful build should be confirmed before claiming production-build validation.

## 9. Live Integration Limitations

The current prototype uses synthetic network telemetry.

The following integrations have not been validated:
- Live IIT Bhubaneswar network devices.
- Production routers and switches.
- Live access point monitoring.
- Packet capture integration.
- Automatic topology discovery.
- Historical network monitoring baselines.

Live campus integration requires authorized access and additional deployment work.

## 10. Final Validation Summary

| Validation item | Recorded status |
|---|---|
| Backend automated tests | PASS — 27/27 |
| Normal telemetry upload | PASS |
| Missing telemetry handling | PASS |
| Five-agent orchestration | PASS in tested diagnosis |
| Synthetic scenario suite | Available; run all scenarios on deployed UI before final demo |
| JSON export | Implemented |
| Evidence CSV export | Implemented |
| PDF print/export | Implemented |
| Frontend production build | Not yet verified |
| Live campus integration | Not implemented |

## 11. Final Notes

NetCoop AI demonstrates a multi-agent network fault diagnosis workflow using synthetic telemetry, structured agent communication, evidence-based correlation, and unified diagnostic reporting.

The system is designed to report uncertainty when available evidence is insufficient rather than making unsupported root-cause claims.

This validation report describes the tests and checks recorded for the prototype. It does not claim production network validation.
