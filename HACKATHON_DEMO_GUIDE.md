# NetCoop AI — Hackathon Demo Guide

## 90-second problem statement
Network operators often receive fragmented telemetry from different network layers. A generic chatbot can produce plausible but unsupported explanations. NetCoop AI separates specialist analysis, anchors measurable findings to deterministic rules, correlates evidence, and makes missing telemetry visible.

## Architecture
1. Telemetry ingestion: CSV/JSON validation and normalization.
2. Performance Agent: latency, jitter, packet loss, throughput, utilization and queue drops.
3. Infrastructure Agent: device status, CPU, memory, interface errors and link flaps only.
4. Connectivity Agent: DNS, DHCP, Wi-Fi signal and retransmissions only.
5. Fault Correlation Agent: merges specialist evidence and checks telemetry coverage.
6. Recommendation Agent: creates operator actions from the correlated diagnosis.
7. Groq: supplementary explanation only; deterministic rules remain authoritative.

## Live demo sequence
1. Register/login to the NetCoop AI workspace.
2. Upload `normal_network.csv`. Explain why the result is `insufficient_data` at 67% coverage: performance and infrastructure are present, connectivity is missing.
3. Upload `weak_wifi_signal.csv`. Show the weak signal/retransmission evidence and affected access points.
4. Upload `link_congestion.csv`. Show utilization/queue-drop evidence and link-congestion classification.
5. Open Reports to show account-scoped incident history.
6. Reopen a report and export evidence CSV or full JSON.

## Expected synthetic scenario results
| Sample | Expected classification |
|---|---|
| normal_network.csv | insufficient_data (connectivity domain missing) |
| link_congestion.csv | investigate — Link congestion |
| weak_wifi_signal.csv | investigate — Weak Wi-Fi signal |
| ethernet_fault.csv | investigate — Ethernet/interface fault |
| dns_dhcp_failure.json | investigate — DNS/DHCP service failure |

## Honest scope statement
This build demonstrates the pipeline on synthetic telemetry. It has not been connected to IIT/campus production switches, routers, access points, packet captures, topology discovery, or historical monitoring systems. For a real deployment, connect authenticated telemetry collectors, map vendor schemas, calibrate thresholds on site data, and validate alert precision/recall.

## Judge questions — short answers
- Why not just a chatbot? The diagnosis is rule/evidence driven; the LLM only explains.
- What if the LLM is wrong? It cannot overwrite deterministic classification, and unsupported claims are filtered.
- What if telemetry is missing? The report shows domain coverage and returns insufficient_data instead of claiming healthy.
- How is the design modular? Specialist agents have explicit metric ownership and receive only their own domain projection.
- Is it live campus monitoring? No. This demo uses synthetic samples; production integration is a next deployment step.
