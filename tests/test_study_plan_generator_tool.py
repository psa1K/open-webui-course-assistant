from __future__ import annotations

import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/study_plan_generator.py"
SCRIPT_PATH = ROOT / "scripts/create_study_plan_generator_tool.py"
CATALOG_PATH = ROOT / "data/course-catalog.json"


def load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
tool_module = load(TOOL_PATH, "study_plan_generator")
tool_module.COURSE_CATALOG_JSON = json.dumps(catalog, ensure_ascii=False)
creator = load(SCRIPT_PATH, "create_study_plan_generator_tool")


class StudyPlanToolTests(unittest.TestCase):
    def setUp(self):
        self.tool = tool_module.Tools()

    def test_has_tools_class_and_public_method(self):
        self.assertTrue(hasattr(tool_module, "Tools"))
        self.assertTrue(callable(getattr(self.tool, "generate_study_plan", None)))

    def test_empty_goal_rejected(self):
        result = self.tool.generate_study_plan()
        self.assertEqual((result["status"], result["error_code"]), ("error", "INVALID_INPUT"))

    def test_invalid_course_rejected(self):
        result = self.tool.generate_study_plan("learn", course="physics")
        self.assertEqual(result["error_code"], "INVALID_INPUT")

    def test_invalid_duration_rejected(self):
        for duration in (0, 53, 1.5, True):
            result = self.tool.generate_study_plan("learn", duration=duration)
            self.assertEqual(result["error_code"], "INVALID_INPUT")

    def test_invalid_duration_unit_rejected(self):
        result = self.tool.generate_study_plan("learn", duration_unit="month")
        self.assertEqual(result["error_code"], "INVALID_INPUT")

    def test_invalid_hours_rejected(self):
        for hours in (0, -1, 169, True):
            result = self.tool.generate_study_plan("learn", hours_per_week=hours)
            self.assertEqual(result["error_code"], "INVALID_INPUT")

    def test_valid_input_returns_ready_request(self):
        result = self.tool.generate_study_plan(
            "掌握 CLI 和 Git 工作流", duration=6, course="codex", student_level="基础", hours_per_week=5,
            preferred_chapters=["CLI", "Git"],
        )
        self.assertEqual((result["status"], result["mode"]), ("ready", "study_plan_generation"))
        request = result["plan_request"]
        self.assertEqual(request["duration"], 6)
        self.assertEqual(request["course"], "codex")
        self.assertEqual(request["preferred_chapters"], ["CLI", "Git"])
        self.assertGreaterEqual(len(result["catalog"]["matched_chapters"]), 1)
        plan = result["study_plan"]
        self.assertEqual(plan["status"], "ok")
        self.assertEqual(plan["total_hours"], 30)
        self.assertTrue(plan["phases"])
        self.assertTrue(plan["sources"])
        self.assertTrue(all(phase["chapters"] for phase in plan["phases"]))

    def test_cross_course_plan_is_supported(self):
        result = self.tool.generate_study_plan("建立综合学习基础", duration=2)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["plan_request"]["course"], None)
        self.assertEqual({c["course"] for c in result["catalog"]["matched_chapters"]}, {"codex", "math-modeling"})

    def test_unknown_chapter_reports_no_basis(self):
        result = self.tool.generate_study_plan("learn", preferred_chapters=["量子计算"])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["catalog"]["matched_chapters"], [])
        self.assertIn("资料中未找到相关信息", result["message"])

    def test_output_instructions_require_catalog_and_json_markdown(self):
        result = self.tool.generate_study_plan("learn", course="codex")
        self.assertTrue(result["instructions"]["generate_from_catalog_only"])
        self.assertTrue(result["instructions"]["include_chapter_sources"])
        self.assertTrue(result["instructions"]["do_not_invent_chapters_or_sources"])
        self.assertEqual(result["instructions"]["output_format"], "json_and_markdown")
        self.assertIn("phases", result["output_schema"])
        self.assertIn("sources", result["output_schema"])

    def test_catalog_sources_are_real(self):
        source_count = 0
        for course in catalog["courses"]:
            for chapter in course["chapters"]:
                source = chapter["source"]
                self.assertTrue((ROOT / source["dir"] / source["file"]).exists())
                source_count += 1
        self.assertGreaterEqual(source_count, 8)

    def test_tool_has_no_network_database_or_secrets(self):
        text = TOOL_PATH.read_text(encoding="utf-8")
        for forbidden in ("httpx", "requests", "sqlite3", "OPENAI_API_KEY", "Bearer ", "password", "subprocess"):
            self.assertNotIn(forbidden, text)


class StudyPlanCreatorTests(unittest.TestCase):
    def test_creator_inlines_catalog(self):
        content = creator.build_content()
        self.assertIn("class Tools:", content)
        self.assertIn("def generate_study_plan(", content)
        self.assertNotIn("PLACEHOLDER_COURSE_CATALOG", content)
        self.assertIn("CX-01", content)
        self.assertIn("MM-01", content)

    def test_payload(self):
        count = sum(len(c["chapters"]) for c in catalog["courses"])
        body = creator.payload("study_plan_generator", "学习计划生成工具", "class Tools:", count)
        self.assertEqual(body["id"], "study_plan_generator")
        self.assertIn(str(count), body["meta"]["description"])


if __name__ == "__main__":
    unittest.main()
