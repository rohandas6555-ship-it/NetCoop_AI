"""Central, configurable thresholds for deterministic telemetry checks.

Interface error/link flap thresholds are positive counter deltas for the
measurement window (not lifetime counter totals). Set via environment vars.
"""
import os

def _number(name: str, default: float, allow_negative: bool = False) -> float:
    try:
        value = float(os.getenv(name, str(default)))
        return value if (allow_negative or value >= 0) else default
    except (TypeError, ValueError):
        return default

THRESHOLDS = {
    "latency_ms": _number("NETCOOP_LATENCY_MS", 100),
    "jitter_ms": _number("NETCOOP_JITTER_MS", 20),
    "packet_loss_pct": _number("NETCOOP_PACKET_LOSS_PCT", 3),
    "link_utilization_pct": _number("NETCOOP_LINK_UTILIZATION_PCT", 85),
    "queue_drops": _number("NETCOOP_QUEUE_DROPS", 0),
    "cpu_usage_pct": _number("NETCOOP_CPU_USAGE_PCT", 90),
    "memory_usage_pct": _number("NETCOOP_MEMORY_USAGE_PCT", 90),
    "interface_errors_delta": _number("NETCOOP_INTERFACE_ERRORS_DELTA", 0),
    "link_flaps_delta": _number("NETCOOP_LINK_FLAPS_DELTA", 0),
    "wifi_signal_dbm": _number("NETCOOP_WIFI_SIGNAL_DBM", -75, allow_negative=True),
    "wifi_retransmissions": _number("NETCOOP_WIFI_RETRANSMISSIONS", 20),
    "dns_query_failures": _number("NETCOOP_DNS_QUERY_FAILURES", 10),
    "dhcp_lease_failures": _number("NETCOOP_DHCP_LEASE_FAILURES", 0),
}
