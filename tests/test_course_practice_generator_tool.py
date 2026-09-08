import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/course_practice_generator.py"
SCRIPT_PATH = ROOT / "scripts/create_course_practice_generator_tool.py"

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tool = load(TOOL_PATH, "course_practice_generator")
creator = load(SCRIPT_PATH, "create_course_practice_generator_tool")


class CourseToolTests(unittest.TestCase):
    def setUp(self):
        self.instance = tool.Tools()

    def test_tools_class_and_method(self):
        self.assertTrue(hasattr(tool, "Tools"))
        self.assertTrue(callable(self.instance.generate_practice_questions))

    def test_empty_chapter_rejected(self):
        result = self.instance.generate_practice_questions(chapter="")
        self.assertEqual((result["status"], result["error_code"]), ("error", "INVALID_INPUT"))

    def test_invalid_course_rejected(self):
        self.assertEqual(self.instance.generate_practice_questions(course="physics", chapter="x")["status"], "error")

    def test_invalid_difficulty_rejected(self):
        self.assertEqual(self.instance.generate_practice_questions(chapter="x", difficulty="expert")["status"], "error")

    def test_count_bounds_rejected(self):
        for count in (0, 11):
            self.assertEqual(self.instance.generate_practice_questions(chapter="x", count=count)["status"], "error")

    def test_valid_input_ready(self):
        result = self.instance.generate_practice_questions(course="codex", chapter="Codex CLI")
        self.assertEqual(result["status"], "ready")

    def test_temporary_mode(self):
        self.assertEqual(self.instance.generate_practice_questions(chapter="x")["mode"], "temporary_generation")

    def test_request_constraints_are_normalized(self):
        request = self.instance.generate_practice_questions(course=" CODEX ", chapter=" CLI ", difficulty=" HARD ", count=2, question_types=[" 简答题 "], student_level="基础", include_answer=True)["generation_request"]
        self.assertEqual(request, {"course": "codex", "chapter": "CLI", "difficulty": "hard", "count": 2, "question_types": ["简答题"], "student_level": "基础", "include_answer": True})

    def test_instructions_require_knowledge_and_no_fabrication(self):
        instructions = self.instance.generate_practice_questions(chapter="x")["instructions"]
        self.assertEqual(instructions["knowledge_source"], "course-knowledge-base")
        self.assertTrue(instructions["use_retrieved_context_only"])
        self.assertTrue(instructions["do_not_invent_sources"])

    def test_json_and_markdown_required(self):
        self.assertEqual(self.instance.generate_practice_questions(chapter="x")["instructions"]["output_format"], "json_and_markdown")

    def test_include_answer_defaults_false(self):
        self.assertFalse(self.instance.generate_practice_questions(chapter="x")["generation_request"]["include_answer"])

    def test_include_answer_policy_is_controlled(self):
        result = self.instance.generate_practice_questions(chapter="x", include_answer=True)
        self.assertIn("参考答案", result["instructions"]["answer_policy"])
        self.assertTrue(result["instructions"]["do_not_generate_complete_submitted_assignment"])

    def test_output_schema_fields(self):
        schema = self.instance.generate_practice_questions(chapter="x")["output_schema"]
        for key in ("status", "course", "chapter", "difficulty", "requested_count", "generated_count", "questions", "sources", "answer_policy"):
            self.assertIn(key, schema)
        for key in ("number", "type", "question", "hint", "knowledge_points", "source"):
            self.assertIn(key, schema["questions"][0])
        self.assertIn("file", schema["questions"][0]["source"])
        self.assertIn("section", schema["questions"][0]["source"])

    def test_tool_has_no_network_database_or_secrets(self):
        text = TOOL_PATH.read_text()
        for forbidden in ("httpx", "requests", "sqlite3", "OPENAI_API_KEY", "Bearer ", "password"):
            self.assertNotIn(forbidden, text)

    def test_creator_validates_source(self):
        self.assertIn("class Tools:", creator.source_content())

    def test_creator_payload_matches_tool(self):
        body = creator.payload("course_practice_generator", "章节练习题生成器", "class Tools:")
        self.assertEqual(body["id"], "course_practice_generator")
        self.assertEqual(body["name"], "章节练习题生成器")

    def test_openwebui_loader_shape(self):
        self.assertTrue(TOOL_PATH.read_text().startswith('"""'))
        self.assertIn("class Tools:", TOOL_PATH.read_text())

    def test_config_matches_parameters_and_rules(self):
        text = (ROOT / "configs/course-tools/course-practice-generator.md").read_text()
        for term in ("temporary_generation", "course", "chapter", "difficulty", "count", "question_types", "student_level", "include_answer", "course-knowledge-base", "JSON", "Markdown", "资料中未找到相关信息"):
            self.assertIn(term, text)

    def test_prompt_contains_temporary_generation_rules(self):
        text = (ROOT / "configs/course-assistant/system-prompt.md").read_text()
        for term in ("不是固定题库", "临时生成", "course-knowledge-base", "资料中未找到相关信息", "结构化 JSON 和 Markdown", "不能代替学生完成整份"):
            self.assertIn(term, text)

    def test_verification_record_is_safe_and_passed(self):
        data = json.loads((ROOT / "docs/tools/verification-results.json").read_text())
        self.assertEqual(data["status"], "passed")
        self.assertNotIn("password", json.dumps(data).lower())
        self.assertNotIn("bearer ", json.dumps(data).lower())


if __name__ == "__main__":
    unittest.main()
