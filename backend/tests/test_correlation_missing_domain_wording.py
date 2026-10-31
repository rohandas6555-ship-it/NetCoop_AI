import unittest
from unittest.mock import patch
from app.agents.correlation_agent import correlate_findings

class CorrelationMissingDomainTests(unittest.TestCase):
    def test_missing_connectivity_is_named_accurately(self):
        rows=[{"device_id":"AP-1","latency_ms":18,"cpu_usage_pct":20}]
        agents=[
          {"agent":"performance_agent","findings":[],"evidence":[],"status":"clear"},
          {"agent":"infrastructure_agent","findings":[],"evidence":[],"status":"clear"},
          {"agent":"connectivity_agent","findings":[],"evidence":[],"status":"insufficient_data"},
        ]
        with patch("app.agents.correlation_agent.analyze_with_groq") as groq:
            groq.return_value={"provider":"groq","status":"completed","output":{"summary":"No diagnostic telemetry domains present","uncertainties":[]}}
            result=correlate_findings(agents,rows)
        self.assertIn("Missing domains: connectivity",result["rationale"])
        self.assertEqual(result["llm_analysis"]["output"]["summary"],result["rationale"])
        self.assertEqual(result["llm_analysis"]["output"]["uncertainties"],["Missing telemetry domain: connectivity"])

if __name__ == "__main__":
    unittest.main()
