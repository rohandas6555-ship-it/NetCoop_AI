# Step 4.5 – Thresholds and DNS/DHCP validation

- Centralized deterministic thresholds in `backend/app/config/thresholds.py`.
- Added environment overrides for latency, jitter, packet loss, utilization, queue drops, CPU, memory, interface-error deltas, link-flap deltas, Wi-Fi, DNS and DHCP.
- Interface errors and link flaps are explicitly treated as positive counter deltas within the measurement window; compare interval deltas, not lifetime totals.
- Prioritized DNS/DHCP service-specific evidence in root-cause correlation so generic infrastructure findings cannot mask a DNS/DHCP fault.
- Added regression tests for threshold behavior and the DNS/DHCP sample.

Run from backend: `python -m unittest discover -s tests -v`.
