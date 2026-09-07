from __future__ import annotations

import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/knowledge_prerequisite_query.py"
SCRIPT_PATH = ROOT / "scripts/create_prerequisite_query_tool.py"
CATALOG_PATH = ROOT / "data/course-catalog.json"
GRAPH_PATH = ROOT / "data/knowledge-prerequisites.json"


def load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
tool_module = load(TOOL_PATH, "knowledge_prerequisite_query")
tool_module.COURSE_CATALOG_JSON = json.dumps(catalog, ensure_ascii=False)
tool_module.PREREQUISITE_GRAPH_JSON = json.dumps(graph, ensure_ascii=False)
creator = load(SCRIPT_PATH, "create_prerequisite_query_tool")


class PrerequisiteQueryTests(unittest.TestCase):
    def setUp(self):
        self.tool = tool_module.Tools()

    def test_has_tools_class_and_public_method(self):
        self.assertTrue(hasattr(tool_module, "Tools"))
        self.assertTrue(callable(getattr(self.tool, "query_prerequisites", None)))

    def test_empty_knowledge_point_rejected(self):
        for value in ("", "   ", None):
            result = self.tool.query_prerequisites(value)
            self.assertEqual((result["status"], result["error_code"]), ("error", "INVALID_INPUT"))

    def test_invalid_course_rejected(self):
        result = self.tool.query_prerequisites("MCP", course="physics")
        self.assertEqual(result["error_code"], "INVALID_INPUT")

    def test_invalid_indirect_flag_rejected(self):
        result = self.tool.query_prerequisites("MCP", include_indirect="yes")
        self.assertEqual(result["error_code"], "INVALID_INPUT")

    def test_kmp_returns_prefix_function_as_prerequisite(self):
        result = self.tool.query_prerequisites("KMP", course="math-modeling")
        self.assertEqual(result["status"], "ok")
        kmp = next(item for item in result["knowledge_points"] if item["id"] == "MM-KP-KMP")
        self.assertEqual([item["id"] for item in kmp["prerequisites"]], ["MM-KP-PREFIX"])
        self.assertTrue(kmp["chapter"]["source"]["file"].endswith("Lecture1.pdf"))

    def test_cli_returns_direct_and_indirect_successors(self):
        result = self.tool.query_prerequisites("CLI 安装", course="codex", include_indirect=True)
        cli = next(item for item in result["knowledge_points"] if item["id"] == "CX-KP-CLI")
        self.assertIn("CX-KP-SANDBOX", {item["id"] for item in cli["successors"]})
        self.assertIn("CX-KP-SERVER", {item["id"] for item in cli["all_successors"]})

    def test_mcp_server_returns_multiple_direct_prerequisites(self):
        result = self.tool.query_prerequisites("MCP Server", course="codex")
        server = next(item for item in result["knowledge_points"] if item["id"] == "CX-KP-SERVER")
        self.assertEqual({item["id"] for item in server["prerequisites"]}, {"CX-KP-MCP", "CX-KP-RULES"})

    def test_unknown_knowledge_point_reports_no_basis(self):
        result = self.tool.query_prerequisites("量子计算", course="codex")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["matched_count"], 0)
        self.assertIn("资料中未找到相关信息", result["message"])

    def test_output_contains_course_chapter_and_source(self):
        result = self.tool.query_prerequisites("组合优化")
        node = result["knowledge_points"][0]
        self.assertEqual(node["course"], "math-modeling")
        self.assertIn("title", node["chapter"])
        self.assertIn("file", node["chapter"]["source"])

    def test_graph_references_real_catalog_chapters_and_materials(self):
        chapter_index = {
            chapter["id"]: chapter
            for course in catalog["courses"]
            for chapter in course["chapters"]
        }
        for node in graph["knowledge_points"]:
            chapter = chapter_index[node["chapter_id"]]
            source = chapter["source"]
            self.assertTrue((ROOT / source["dir"] / source["file"]).exists())

    def test_tool_has_no_network_database_or_secrets(self):
        text = TOOL_PATH.read_text(encoding="utf-8")
        for forbidden in ("httpx", "requests.", "sqlite3", "OPENAI_API_KEY", "Bearer ", "password", "subprocess"):
            self.assertNotIn(forbidden, text)


class PrerequisiteCreatorTests(unittest.TestCase):
    def test_creator_validates_and_inlines_both_datasets(self):
        content = creator.build_content()
        self.assertIn("class Tools:", content)
        self.assertIn("def query_prerequisites(", content)
        self.assertNotIn("PLACEHOLDER_COURSE_CATALOG", content)
        self.assertNotIn("PLACEHOLDER_PREREQUISITE_GRAPH", content)
        self.assertIn("CX-KP-MCP", content)
        self.assertIn("MM-KP-KMP", content)

    def test_creator_payload(self):
        body = creator.payload("knowledge_prerequisite_query", "知识点先修关系查询工具", "class Tools:", 22, 20)
        self.assertEqual(body["id"], "knowledge_prerequisite_query")
        self.assertIn("22", body["meta"]["description"])
        self.assertIn("20", body["meta"]["description"])


if __name__ == "__main__":
    unittest.main()
