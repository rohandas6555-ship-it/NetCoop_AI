import csv
import json
import unittest
from pathlib import Path
from app.orchestration.diagnosis_orchestrator import run_diagnosis
from app.services.telemetry_quality_service import assess_telemetry_quality

SAMPLES = Path(__file__).resolve().parents[2] / "frontend" / "public" / "samples"


def load_sample(name):
    path = SAMPLES / name
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class Step43Tests(unittest.TestCase):
    def test_normal_is_not_declared_fully_healthy_with_missing_domain(self):
        report = run_diagnosis(load_sample("normal_network.csv"), "INC-TEST", "normal_network.csv", "Auto")
        self.assertEqual(report["status"], "insufficient_data")
        self.assertIn("connectivity", report["telemetry_coverage"]["missing_groups"])

    def test_link_congestion(self):
        report = run_diagnosis(load_sample("link_congestion.csv"), "INC-TEST", "link_congestion.csv", "Auto")
        self.assertEqual(report["status"], "investigate")
        self.assertEqual(report["suspected_root_cause"], "Link congestion")

    def test_weak_wifi(self):
        report = run_diagnosis(load_sample("weak_wifi_signal.csv"), "INC-TEST", "weak_wifi_signal.csv", "Auto")
        self.assertEqual(report["suspected_root_cause"], "Weak Wi-Fi signal")

    def test_ethernet_fault(self):
        report = run_diagnosis(load_sample("ethernet_fault.csv"), "INC-TEST", "ethernet_fault.csv", "Auto")
        self.assertEqual(report["suspected_root_cause"], "Ethernet/interface fault")

    def test_dns_dhcp_failure(self):
        report = run_diagnosis(load_sample("dns_dhcp_failure.json"), "INC-TEST", "dns_dhcp_failure.json", "Auto")
        self.assertEqual(report["suspected_root_cause"], "DNS/DHCP service failure")


    def test_quality_flags_invalid_numeric_values_and_unknown_columns(self):
        quality = assess_telemetry_quality([{"device_id": "SW-1", "latency_ms": "fast", "mystery": "x"}])
        self.assertEqual(quality["quality_status"], "warning")
        self.assertEqual(len(quality["invalid_numeric_values"]), 1)
        self.assertIn("mystery", quality["unknown_columns"])

    def test_report_includes_telemetry_quality(self):
        report = run_diagnosis(load_sample("normal_network.csv"), "INC-TEST", "normal_network.csv", "Auto")
        self.assertIn("telemetry_quality", report)
        self.assertIn("quality_status", report["telemetry_quality"])

    def test_empty_records_rejected(self):
        with self.assertRaises(ValueError):
            run_diagnosis([], "INC-TEST", "empty.csv", "Auto")

    def test_groq_default_model_is_configured(self):
        service = (Path(__file__).resolve().parents[1] / "app" / "llm" / "groq_service.py").read_text(encoding="utf-8")
        self.assertIn('os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")', service)
        self.assertIn('response_format={"type":"json_object"}', service)


if __name__ == "__main__":
    unittest.main()
