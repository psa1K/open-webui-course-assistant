import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/course_catalog_query.py"
SCRIPT_PATH = ROOT / "scripts/create_course_catalog_tool.py"
CATALOG_PATH = ROOT / "data/course-catalog.json"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_embedded_tool():
    creator = load(SCRIPT_PATH, f"create_course_catalog_tool_{id(object())}")
    content = creator.build_content()
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(content)
        tmp = Path(fh.name)
    try:
        return load(tmp, f"course_catalog_query_{id(object())}")
    finally:
        tmp.unlink()


tool = load_embedded_tool()
creator = load(SCRIPT_PATH, "create_course_catalog_tool")
catalog_data = json.loads(CATALOG_PATH.read_text())


def all_sources():
    for course in catalog_data["courses"]:
        for ch in course["chapters"]:
            yield ch["source"], course["id"]


class CourseCatalogQueryTests(unittest.TestCase):
    def setUp(self):
        self.instance = tool.Tools()

    def test_tools_class_and_methods(self):
        self.assertTrue(hasattr(tool, "Tools"))
        self.assertTrue(callable(self.instance.query_chapter))
        self.assertTrue(callable(self.instance.list_chapters))

    def test_query_by_chapter_title(self):
        result = self.instance.query_chapter("Codex CLI 安装与上手")
        self.assertEqual(result["status"], "ok")
        self.assertGreaterEqual(result["matched_count"], 1)
        self.assertEqual(result["chapters"][0]["id"], "CX-06")

    def test_query_by_keyword_knowledge_point(self):
        result = self.instance.query_chapter("MCP")
        self.assertGreaterEqual(result["matched_count"], 1)
        ids = {ch["id"] for ch in result["chapters"]}
        self.assertIn("CX-12", ids)

    def test_query_by_english_keyword(self):
        result = self.instance.query_chapter("KMP")
        ids = {ch["id"] for ch in result["chapters"]}
        self.assertIn("MM-01", ids)

    def test_query_case_insensitive(self):
        a = self.instance.query_chapter("kmp")
        b = self.instance.query_chapter("KMP")
        self.assertEqual([ch["id"] for ch in a["chapters"]], [ch["id"] for ch in b["chapters"]])

    def test_query_scoped_to_course(self):
        result = self.instance.query_chapter("KMP", course="math-modeling")
        self.assertGreaterEqual(result["matched_count"], 1)
        for ch in result["chapters"]:
            self.assertEqual(ch["course"], "math-modeling")

    def test_query_rank_title_above_section(self):
        result = self.instance.query_chapter("组合优化")
        self.assertGreaterEqual(result["matched_count"], 1)
        self.assertEqual(result["chapters"][0]["id"], "MM-04")

    def test_query_no_match(self):
        result = self.instance.query_chapter("量子计算")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["chapters"], [])

    def test_query_empty_keyword_rejected(self):
        for bad in ("", "   ", None):
            self.assertEqual(self.instance.query_chapter(bad)["error_code"], "INVALID_INPUT")

    def test_query_invalid_course_rejected(self):
        self.assertEqual(self.instance.query_chapter("MCP", course="physics")["error_code"], "INVALID_INPUT")

    def test_result_contains_knowledge_points_and_source(self):
        result = self.instance.query_chapter("沙盒")
        self.assertGreaterEqual(result["matched_count"], 1)
        ch = result["chapters"][0]
        self.assertTrue(ch["knowledge_points"])
        self.assertIn("file", ch["source"])
        self.assertIn("dir", ch["source"])

    def test_list_all_courses(self):
        result = self.instance.list_chapters()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["course_count"], 2)
        ids = {c["id"] for c in result["courses"]}
        self.assertEqual(ids, {"codex", "math-modeling"})

    def test_list_scoped_course(self):
        result = self.instance.list_chapters(course="codex")
        self.assertEqual(result["course_count"], 1)
        self.assertEqual(result["courses"][0]["id"], "codex")
        self.assertEqual(result["courses"][0]["chapter_count"], 16)

    def test_list_invalid_course_rejected(self):
        self.assertEqual(self.instance.list_chapters(course="nope")["error_code"], "INVALID_INPUT")


class CourseCatalogDataTests(unittest.TestCase):
    def test_sources_exist_in_knowledge(self):
        for source, _course in all_sources():
            path = ROOT / source["dir"] / source["file"]
            self.assertTrue(path.exists(), f"目录来源不存在: {path}")

    def test_catalog_covers_both_courses_and_enough_chapters(self):
        courses = {c["id"] for c in catalog_data["courses"]}
        self.assertEqual(courses, {"codex", "math-modeling"})
        total = sum(len(c["chapters"]) for c in catalog_data["courses"])
        self.assertGreaterEqual(total, 20)

    def test_chapter_ids_unique(self):
        seen = []
        for course in catalog_data["courses"]:
            for ch in course["chapters"]:
                seen.append(ch["id"])
        self.assertEqual(len(seen), len(set(seen)))


class CourseCatalogToolTests(unittest.TestCase):
    def test_tool_has_no_network_database_or_secrets(self):
        text = TOOL_PATH.read_text()
        for forbidden in ("httpx", "requests.", "sqlite3", "OPENAI_API_KEY", "password", "subprocess"):
            self.assertNotIn(forbidden, text)

    def test_creator_inlines_catalog_into_content(self):
        content = creator.build_content()
        self.assertIn("class Tools:", content)
        self.assertIn("def query_chapter(", content)
        self.assertNotIn("PLACEHOLDER_COURSE_CATALOG", content)
        self.assertIn("CX-01", content)
        self.assertIn("MM-01", content)

    def test_creator_payload(self):
        total = sum(len(c["chapters"]) for c in catalog_data["courses"])
        body = creator.payload("course_catalog_query", "课程章节查询工具", "class Tools:", total)
        self.assertEqual(body["id"], "course_catalog_query")
        self.assertIn("课程目录", body["meta"]["description"])


if __name__ == "__main__":
    unittest.main()
