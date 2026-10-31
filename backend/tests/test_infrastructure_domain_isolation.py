import unittest
from unittest.mock import patch
from app.agents.infrastructure_agent import analyze_infrastructure
from app.agents.correlation_agent import _coverage

class InfrastructureDomainIsolationTests(unittest.TestCase):
    def test_performance_only_data_skips_infrastructure_groq(self):
        rows=[{"device_id":"SW-1","latency_ms":180,"packet_loss_pct":4,
               "throughput_mbps":100,"link_utilization_pct":90,"queue_drops":12}]
        with patch("app.llm.groq_service.analyze_with_groq") as groq:
            result=analyze_infrastructure(rows)
        self.assertEqual(result["status"],"insufficient_data")
        self.assertEqual(result["llm_analysis"]["status"],"skipped")
        groq.assert_not_called()

    def test_groq_payload_contains_only_infrastructure_metrics(self):
        rows=[{"device_id":"SW-1","cpu_usage_pct":95,"memory_usage_pct":88,
               "latency_ms":250,"jitter_ms":40,"packet_loss_pct":8,
               "throughput_mbps":20,"link_utilization_pct":99,"queue_drops":100,
               "signal_strength_dbm":-80,"service":"DNS","query_failures":50}]
        with patch("app.llm.groq_service.analyze_with_groq") as groq:
            groq.return_value={"provider":"groq","status":"completed","output":{}}
            result=analyze_infrastructure(rows)
        payload=str(groq.call_args.args[2])
        for forbidden in ("latency_ms","jitter_ms","packet_loss_pct","throughput_mbps",
                          "link_utilization_pct","queue_drops","signal_strength_dbm",
                          "query_failures","service"):
            self.assertNotIn(forbidden,payload)
        self.assertEqual(result["status"],"findings")

    def test_dns_service_status_does_not_count_as_infrastructure(self):
        coverage=_coverage([{"device_id":"DNS-1","service":"DNS","status":"failed","query_failures":10}])
        self.assertNotIn("infrastructure",coverage["available_groups"])
        self.assertIn("connectivity",coverage["available_groups"])

    def test_empty_infrastructure_values_are_missing(self):
        result=analyze_infrastructure([{"device_id":"SW-1","cpu_usage_pct":None,
                                        "memory_usage_pct":"","interface_errors":None}])
        self.assertEqual(result["status"],"insufficient_data")

if __name__ == "__main__":
    unittest.main()
