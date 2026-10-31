import unittest
from unittest.mock import patch
from app.agents.connectivity_agent import analyze_connectivity

class ConnectivityDomainIsolationTests(unittest.TestCase):
    def test_performance_only_payload_is_insufficient_and_skips_groq(self):
        rows=[{"device_id":"AP-1","latency_ms":18,"packet_loss_pct":0,"jitter_ms":2,"queue_drops":0,"cpu_usage_pct":20}]
        with patch("app.llm.groq_service.analyze_with_groq") as groq:
            result=analyze_connectivity(rows)
        self.assertEqual(result["status"],"insufficient_data")
        self.assertEqual(result["llm_analysis"]["status"],"skipped")
        groq.assert_not_called()

    def test_groq_receives_only_connectivity_fields(self):
        rows=[{"device_id":"AP-1","service":"WIFI","signal_strength_dbm":-82,"latency_ms":180,
               "packet_loss_pct":8,"queue_drops":99,"cpu_usage_pct":91,"interface_errors":7}]
        with patch("app.llm.groq_service.analyze_with_groq") as groq:
            groq.return_value={"provider":"groq","status":"completed","output":{}}
            result=analyze_connectivity(rows)
        payload=str(groq.call_args.args[2])
        for forbidden in ("latency_ms","packet_loss_pct","queue_drops","cpu_usage_pct","interface_errors"):
            self.assertNotIn(forbidden,payload)
        self.assertEqual(result["status"],"findings")

    def test_empty_connectivity_values_are_missing(self):
        result=analyze_connectivity([{"device_id":"AP-1","service":"","signal_strength_dbm":None,"retransmissions":""}])
        self.assertEqual(result["status"],"insufficient_data")

    def test_wired_interface_errors_are_not_connectivity_findings(self):
        result=analyze_connectivity([{"device_id":"SW-1","interface_errors":20,"link_flaps":2}])
        self.assertEqual(result["status"],"insufficient_data")
        self.assertEqual(result["findings"],[])

if __name__ == "__main__":
    unittest.main()
