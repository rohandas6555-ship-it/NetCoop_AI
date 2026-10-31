import unittest
from app.llm.groq_service import _sanitize_qualitative_claims
class EvidenceGroundingTests(unittest.TestCase):
 def test_removes_claim_about_metric_not_collected(self):
  cleaned={"summary":"Both devices show normal CPU. No evidence of interface errors. No evidence of link flaps.","possible_impacts":[],"follow_up_checks":[]}
  result,removed=_sanitize_qualitative_claims(cleaned,{"telemetry":[{"cpu_usage_pct":28,"latency_ms":18}]})
  self.assertEqual(removed,2); self.assertIn("normal CPU",result["summary"]); self.assertNotIn("interface errors",result["summary"])
 def test_keeps_claim_when_metric_is_present(self):
  cleaned={"summary":"No interface errors were observed.","possible_impacts":[],"follow_up_checks":[]}
  result,removed=_sanitize_qualitative_claims(cleaned,{"telemetry":[{"interface_errors":0}]})
  self.assertEqual(removed,0); self.assertIn("No interface errors",result["summary"])
 def test_missing_wifi_data_does_not_allow_wifi_assessment(self):
  cleaned={"summary":"Wi-Fi signal is healthy.","possible_impacts":[],"follow_up_checks":[]}
  result,removed=_sanitize_qualitative_claims(cleaned,{"telemetry":[{"latency_ms":20}]})
  self.assertEqual(removed,1); self.assertIn("omitted",result["summary"])
if __name__=="__main__": unittest.main()
