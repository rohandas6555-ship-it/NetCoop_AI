import unittest
from app.llm.groq_service import _sanitize_evidence_claims

class DomainGuardTests(unittest.TestCase):
    def test_blocks_connectivity_health_claim_when_domain_missing(self):
        data = {"summary":"Latency is low. No connectivity issues detected.",
                "possible_impacts":["Connectivity is healthy."],
                "follow_up_checks":["Collect DNS and DHCP telemetry."]}
        result, removed = _sanitize_evidence_claims(data, {"telemetry":[{"latency_ms":18,"packet_loss_pct":0.1}]})
        self.assertEqual(removed, 2)
        self.assertEqual(result["summary"], "Latency is low.")
        self.assertEqual(result["possible_impacts"], [])
        self.assertEqual(result["follow_up_checks"], ["Collect DNS and DHCP telemetry."])

    def test_allows_connectivity_claim_when_connectivity_metrics_exist(self):
        data = {"summary":"No connectivity issues detected.", "possible_impacts":[], "follow_up_checks":[]}
        result, removed = _sanitize_evidence_claims(data, {"telemetry":[{"service":"DNS","query_failures":0}]})
        self.assertEqual(removed, 0)
        self.assertIn("No connectivity issues", result["summary"])

    def test_blocks_wifi_health_without_wifi_metrics(self):
        data = {"summary":"Wi-Fi signal is healthy.", "possible_impacts":[], "follow_up_checks":[]}
        result, removed = _sanitize_evidence_claims(data, {"telemetry":[{"latency_ms":18}]})
        self.assertEqual(removed, 1)
        self.assertIn("omitted", result["summary"])

if __name__ == "__main__":
    unittest.main()
