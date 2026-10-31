import unittest
from app.config.thresholds import THRESHOLDS
from app.agents.infrastructure_agent import analyze_infrastructure
from app.orchestration.diagnosis_orchestrator import run_diagnosis
import json
from pathlib import Path

SAMPLES = Path(__file__).resolve().parents[2] / "frontend" / "public" / "samples"

def load_json(name):
    return json.loads((SAMPLES / name).read_text(encoding="utf-8"))

class ReliabilityThresholdTests(unittest.TestCase):
    def test_thresholds_are_centralized_and_non_negative_except_wifi_dbm(self):
        self.assertEqual(THRESHOLDS["interface_errors_delta"], 0)
        self.assertEqual(THRESHOLDS["link_flaps_delta"], 0)
        self.assertEqual(THRESHOLDS["latency_ms"], 100)

    def test_interface_error_and_flap_evidence_exposes_thresholds(self):
        result = analyze_infrastructure([{"device_id":"SW-1","interface_errors":12,"link_flaps":3}])
        self.assertTrue(any("interface errors" in x for x in result["findings"]))
        self.assertTrue(any("link flaps" in x for x in result["findings"]))

    def test_dns_dhcp_sample_classified_correctly(self):
        report = run_diagnosis(load_json("dns_dhcp_failure.json"), "INC-DNS-TEST", "dns_dhcp_failure.json", "DNS/DHCP")
        self.assertEqual(report["status"], "investigate")
        self.assertEqual(report["suspected_root_cause"], "DNS/DHCP service failure")
        self.assertEqual(set(report["affected_devices"]), {"DNS_SERVER_01", "DHCP_SERVER_01"})

if __name__ == "__main__":
    unittest.main()
