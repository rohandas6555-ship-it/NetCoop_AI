import unittest
from app.llm.groq_service import _sanitize_numeric_claims


class GroqNumericGuardTests(unittest.TestCase):
    def test_preserves_grounded_numeric_claims(self):
        cleaned = {
            "summary": "Latency reached 280 ms. The uplink is congested.",
            "possible_impacts": ["Packet loss reached 8%"],
            "follow_up_checks": [],
        }
        result, removed = _sanitize_numeric_claims(
            cleaned, {"telemetry": [{"latency_ms": 280, "packet_loss_pct": 8}]}
        )
        self.assertEqual(removed, 0)
        self.assertIn("280 ms", result["summary"])
        self.assertEqual(result["possible_impacts"], ["Packet loss reached 8%"])

    def test_removes_only_unsupported_numeric_sentence_and_list_item(self):
        cleaned = {
            "summary": "Latency reached 280 ms. The issue may affect users in 24 buildings.",
            "possible_impacts": ["Packet loss reached 8%", "Impact may last 45 minutes"],
            "follow_up_checks": ["Inspect the uplink"]
        }
        result, removed = _sanitize_numeric_claims(
            cleaned, {"telemetry": [{"latency_ms": 280, "packet_loss_pct": 8}]}
        )
        self.assertEqual(removed, 2)
        self.assertEqual(result["summary"], "Latency reached 280 ms.")
        self.assertEqual(result["possible_impacts"], ["Packet loss reached 8%"])
        self.assertEqual(result["follow_up_checks"], ["Inspect the uplink"])

    def test_does_not_flag_numbers_present_in_thresholds(self):
        cleaned = {"summary": "Latency is above the 100 ms threshold.", "possible_impacts": [], "follow_up_checks": []}
        result, removed = _sanitize_numeric_claims(cleaned, {"thresholds": {"latency_ms": 100}})
        self.assertEqual(removed, 0)
        self.assertIn("100 ms", result["summary"])


if __name__ == "__main__":
    unittest.main()
