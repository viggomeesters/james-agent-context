from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate_module = load_module("validate", ROOT / "scripts" / "validate.py")
boundary_module = load_module("public_boundary", ROOT / "scripts" / "public_boundary.py")


class GraphContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads((ROOT / "data" / "graph.json").read_text())
        cls.sources = json.loads((ROOT / "data" / "sources.json").read_text())

    def test_source_integrity(self):
        self.assertEqual(validate_module.validate(self.graph, self.sources), [])
        self.assertEqual(len({item["id"] for item in self.sources["sources"]}), len(self.sources["sources"]))

    def test_fact_and_inference_are_distinct(self):
        evidence = {item["evidence_type"] for item in self.graph["entities"] + self.graph["relationships"] + self.graph["claims"]}
        self.assertEqual(evidence, {"fact", "inference"})
        altered = copy.deepcopy(self.graph)
        altered["claims"][0]["evidence_type"] = "unknown"
        self.assertTrue(any("evidence_type" in message for message in validate_module.validate(altered, self.sources)))

    def test_physical_schema_is_explicitly_unknown(self):
        unknown_text = " ".join(item["statement"].lower() for item in self.graph["unknowns"])
        for term in ("database", "table", "primary key", "backend", "endpoint"):
            self.assertIn(term, unknown_text)
        public_records = self.graph["entities"] + self.graph["relationships"] + self.graph["claims"]
        self.assertFalse(any("sql schema" in json.dumps(item).lower() for item in public_records))

    def test_schema_rejects_unknown_payload_and_source_fields(self):
        for field in ("excerpt", "transcript", "source_snapshot", "internal_path"):
            altered_graph = copy.deepcopy(self.graph)
            altered_graph["entities"][0][field] = "A compact copied paragraph with no special marker."
            graph_errors = validate_module.validate(altered_graph, self.sources)
            self.assertTrue(any("unknown fields" in message for message in graph_errors), (field, graph_errors))

        altered_sources = copy.deepcopy(self.sources)
        altered_sources["sources"][0]["source_snapshot"] = "arbitrary payload"
        source_errors = validate_module.validate(self.graph, altered_sources)
        self.assertTrue(any("unknown fields" in message for message in source_errors), source_errors)

    def test_internal_path_is_rejected_in_neutral_field_value(self):
        altered = copy.deepcopy(self.graph)
        altered["entities"][0]["summary"] = "/" + "srv/james" + "/" + "private/archive"
        errors = validate_module.validate(altered, self.sources)
        self.assertTrue(any("forbidden absolute internal path" in message for message in errors), errors)

    def test_full_candidate_tree_scan_and_path_secret_regressions(self):
        paths = boundary_module.candidates()
        names = {boundary_module.display_path(path) for path in paths}
        self.assertTrue({"Makefile", "LICENSE", "scripts/validate.py", "schemas/graph.schema.json", "tests/test_graph.py", ".go/project.json"} <= names)
        self.assertEqual(boundary_module.scan(paths), [])
        tagged_secret_line = "api" + "_key = \"synthetic-audit-secret\" # PUBLIC_" + "BOUNDARY_PATTERN_EXEMPTION"
        tagged_findings = boundary_module.line_findings(ROOT / "tests" / "test_graph.py", tagged_secret_line, 999)
        self.assertTrue(any("secret" in item for item in tagged_findings), tagged_findings)
        with tempfile.TemporaryDirectory() as temp:
            probe = Path(temp) / "probe.txt"
            probe.write_text("/" + "srv/james" + "/" + "private/archive\napi" + "_key = synthetic", encoding="utf-8")
            findings = boundary_module.scan([probe])
            self.assertTrue(any("internal-path" in item for item in findings), findings)
            self.assertTrue(any("secret" in item for item in findings), findings)


if __name__ == "__main__":
    unittest.main()
