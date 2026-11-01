# NetCoop AI — Hackathon Demo Guide

## 1. Project Overview

NetCoop AI is a multi-agent network fault diagnosis system designed to analyze network telemetry, identify probable network issues, correlate findings from specialized agents, and generate evidence-based diagnostic reports.

The system uses a hybrid approach:
- Deterministic rule-based analysis for measurable findings.
- Groq-powered LLM interpretation for supplementary explanations.
- Multi-agent orchestration to combine specialist findings.
- Structured reports with evidence, uncertainty, and recommendations.

## 2. Problem Statement

Network operators often face difficulties diagnosing issues such as:
- High latency and packet loss.
- Network congestion.
- Weak Wi-Fi signals.
- Ethernet interface failures.
- DNS and DHCP service failures.
- Incomplete or inconsistent telemetry.

Relevant information may be distributed across different network components. NetCoop AI addresses this challenge through specialized agents that analyze different telemetry domains and collaborate on a unified diagnosis.

## 3. Multi-Agent Architecture

The system contains five specialized agents.

### 1. Performance Agent
Analyzes:
- Latency
- Jitter
- Packet loss
- Throughput
- Link utilization
- Queue drops

### 2. Infrastructure Agent
Analyzes:
- Device status
- CPU utilization
- Memory utilization
- Interface errors
- Link flaps

### 3. Connectivity Agent
Analyzes:
- DNS and DHCP failures
- Wi-Fi signal strength
- Retransmissions
- Connectivity-related failures

### 4. Fault Correlation Agent
- Receives findings from specialist agents.
- Correlates evidence across telemetry domains.
- Evaluates missing telemetry coverage.
- Identifies probable root causes.
- Reports uncertainty when evidence is insufficient.

### 5. Recommendation Agent
- Receives the correlated diagnosis.
- Generates corrective actions.
- Provides practical troubleshooting recommendations.

## 4. Agent Communication and Orchestration

The workflow follows this sequence:

1. Telemetry is uploaded in CSV or JSON format.
2. The validation service checks the input structure and data quality.
3. Telemetry is normalized and passed to specialist agents.
4. Each specialist agent analyzes its assigned metrics.
5. Findings and evidence are passed to the Fault Correlation Agent.
6. The Recommendation Agent receives the correlated diagnosis.
7. The orchestrator generates a unified diagnostic report.

Each agent has defined metric ownership to prevent unrelated telemetry from influencing its analysis.

## 5. Live Demo Sequence

### Step 1 — Open the Application
Open the deployed NetCoop AI dashboard and log in.

### Step 2 — Upload Normal Telemetry
Upload `normal_network.csv`.

Expected result:
- Performance: Clear.
- Infrastructure: Clear.
- Connectivity: Insufficient data.
- Overall diagnosis: Insufficient data because connectivity telemetry is missing.

Explain that the system does not declare the entire network healthy when telemetry coverage is incomplete.

### Step 3 — Demonstrate Weak Wi-Fi Signal
Upload `weak_wifi_signal.csv`.

Expected classification: Investigate — Weak Wi-Fi signal.

Show the available signal-strength and retransmission evidence.

### Step 4 — Demonstrate Link Congestion
Upload `link_congestion.csv`.

Expected classification: Investigate — Link congestion.

Show utilization, latency, and queue-drop evidence where available.

### Step 5 — Demonstrate Ethernet Fault
Upload `ethernet_fault.csv`.

Expected classification: Investigate — Ethernet/interface fault.

Show the relevant interface and link-health evidence.

### Step 6 — Demonstrate DNS/DHCP Failure
Upload `dns_dhcp_failure.json`.

Expected classification: Investigate — DNS/DHCP service failure.

Show the service-specific connectivity findings.

### Step 7 — Show the Final Report
Demonstrate:
- Incident ID
- Probable root cause
- Confidence score
- Affected devices
- Supporting evidence
- Telemetry coverage
- Recommended actions
- AI interpretation status

### Step 8 — Export Reports
Demonstrate:
- Export JSON
- Export evidence CSV
- Print / Save PDF

## 6. Expected Synthetic Scenario Results

| Sample file | Expected classification |
|---|---|
| normal_network.csv | insufficient_data |
| link_congestion.csv | investigate — Link congestion |
| weak_wifi_signal.csv | investigate — Weak Wi-Fi signal |
| ethernet_fault.csv | investigate — Ethernet/interface fault |
| dns_dhcp_failure.json | investigate — DNS/DHCP service failure |

Actual results depend on the telemetry fields and configured diagnostic thresholds.

## 7. Important Features

- CSV and JSON telemetry ingestion.
- Input validation and schema diagnostics.
- Five specialized agents.
- Structured agent orchestration.
- Evidence-based fault correlation.
- Missing telemetry detection.
- Groq LLM integration.
- Confidence and uncertainty reporting.
- User authentication.
- Incident history.
- JSON, CSV and PDF report export.

## 8. Honest Scope and Limitations

This prototype demonstrates network diagnosis using synthetic telemetry.

It has not been connected to IIT Bhubaneswar's production network, live campus switches, routers, access points, packet captures, topology discovery, or historical monitoring systems.

The confidence value is a heuristic score, not a calibrated probability.

Groq provides supplementary interpretation. Deterministic rules remain authoritative for measurable findings and root-cause classification.

Future production deployment would require authorized telemetry collectors, vendor-specific schema integration, site-calibrated thresholds, and validation against real network incidents.

## 9. Common Jury Questions

**Q1. Why use multiple agents instead of one chatbot?**

Each agent has a specialized responsibility. Their findings are combined to produce a more structured and explainable diagnosis.

**Q2. What happens if the AI gives an incorrect result?**

Deterministic rules establish measurable findings. Unsupported AI claims are filtered, and the AI cannot overwrite deterministic classifications.

**Q3. What happens when telemetry is missing?**

The system identifies missing domains and reports insufficient data instead of making unsupported claims.

**Q4. Is this connected to the live IIT campus network?**

No. The current prototype uses synthetic telemetry. Live campus integration is a future deployment step.

**Q5. How do you evaluate diagnostic reliability?**

Through automated tests, synthetic fault scenarios, telemetry validation, evidence checks, and missing-data handling.

**Q6. What makes NetCoop AI different from a normal support chatbot?**

It uses specialized agents, structured information exchange, deterministic diagnostic rules, evidence correlation, and explainable reports.

## 10. Closing Statement

NetCoop AI demonstrates how multiple specialized agents can collaborate to make network troubleshooting more explainable, reliable, and efficient.

The primary innovation is not simply using AI to detect a fault, but enabling agents to exchange findings, correlate evidence, handle uncertainty, and generate one coherent diagnostic result.
