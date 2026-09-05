import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/random_question_picker.py"
SCRIPT_PATH = ROOT / "scripts/create_random_picker_tool.py"
BANK_PATH = ROOT / "data/question-bank.json"
COURSE_DIR = {"codex": "knowledge/codex-course", "math-modeling": "knowledge/math-modeling"}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_embedded_tool():
    """Load the tool with the question bank inlined, as the installer does."""
    creator = load(SCRIPT_PATH, f"create_random_picker_tool_{id(object())}")
    content = creator.build_content()
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(content)
        tmp = Path(fh.name)
    try:
        return load(tmp, f"random_question_picker_{id(object())}")
    finally:
        tmp.unlink()


tool = load_embedded_tool()
creator = load(SCRIPT_PATH, "create_random_picker_tool")
bank_data = json.loads(BANK_PATH.read_text())


class RandomPickerToolTests(unittest.TestCase):
    def setUp(self):
        self.instance = tool.Tools()

    def pick(self, **kwargs):
        return self.instance.pick_random_questions(**kwargs)

    def test_tools_class_and_method(self):
        self.assertTrue(hasattr(tool, "Tools"))
        self.assertTrue(callable(self.instance.pick_random_questions))

    def test_valid_pick_returns_real_bank_question(self):
        result = self.pick(course="codex", chapter="CLI", count=2)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mode"], "random_pick_from_bank")
        self.assertEqual(result["picked_count"], 2)
        for q in result["questions"]:
            self.assertTrue(q["source"]["file"])
            self.assertTrue(q["id"])

    def test_no_answer_by_default(self):
        result = self.pick(chapter="KMP")
        self.assertFalse(result["constraints"]["include_answer"])
        for q in result["questions"]:
            self.assertNotIn("reference_answer", q)

    def test_include_answer_returns_reference_for_choice(self):
        result = self.pick(chapter="KMP", count=1, include_answer=True, seed=7)
        q = result["questions"][0]
        self.assertIn("reference_answer", q)
        expected = next(b for b in bank_data["questions"] if b["id"] == q["id"])
        if "options" in expected:
            self.assertEqual(q["reference_answer"], expected["options"][expected["answer_index"]])
        else:
            self.assertIn("参考要点", q["reference_answer"])

    def test_include_answer_choice_question_returns_exact_option(self):
        result = self.pick(chapter="认识 Codex", difficulty="easy", count=1, include_answer=True, seed=1)
        q = result["questions"][0]
        expected = next(b for b in bank_data["questions"] if b["id"] == q["id"])
        self.assertIn("options", expected)
        self.assertEqual(q["reference_answer"], expected["options"][expected["answer_index"]])

    def test_seed_is_reproducible(self):
        a = self.pick(count=3, seed=42)
        b = self.pick(count=3, seed=42)
        self.assertEqual([q["id"] for q in a["questions"]], [q["id"] for q in b["questions"]])
        c = self.pick(count=3, seed=43)
        self.assertNotEqual([q["id"] for q in a["questions"]], [q["id"] for q in c["questions"]])

    def test_invalid_course_rejected(self):
        self.assertEqual(self.pick(course="physics")["error_code"], "INVALID_INPUT")

    def test_invalid_difficulty_rejected(self):
        self.assertEqual(self.pick(difficulty="expert")["error_code"], "INVALID_INPUT")

    def test_invalid_question_type_rejected(self):
        self.assertEqual(self.pick(question_type="填空题")["error_code"], "INVALID_INPUT")

    def test_count_bounds_rejected(self):
        for count in (0, 11, 1.5, True):
            self.assertEqual(self.pick(count=count)["error_code"], "INVALID_INPUT")

    def test_no_matching_questions_reported(self):
        result = self.pick(course="math-modeling", question_type="代码题")
        self.assertEqual((result["status"], result["error_code"]), ("error", "NO_MATCHING_QUESTIONS"))
        self.assertEqual(result["bank_size"], len(bank_data["questions"]))

    def test_chapter_fuzzy_match(self):
        result = self.pick(chapter="MCP", count=5)
        for q in result["questions"]:
            self.assertIn("MCP", q["chapter"])

    def test_source_files_exist_in_knowledge(self):
        for q in bank_data["questions"]:
            path = ROOT / COURSE_DIR[q["course"]] / q["source"]["file"]
            self.assertTrue(path.exists(), f"题库来源不存在: {path}")

    def test_bank_covers_two_courses_and_three_difficulties(self):
        bank = bank_data["questions"]
        self.assertGreaterEqual(len(bank), 20)
        self.assertEqual({q["course"] for q in bank}, {"codex", "math-modeling"})
        self.assertEqual({q["difficulty"] for q in bank}, {"easy", "medium", "hard"})
        self.assertGreaterEqual(len({q["type"] for q in bank}), 4)

    def test_tool_has_no_network_database_or_secrets(self):
        text = TOOL_PATH.read_text()
        for forbidden in ("httpx", "requests", "sqlite3", "OPENAI_API_KEY", "Bearer ", "password"):
            self.assertNotIn(forbidden, text)

    def test_creator_inlines_bank_into_content(self):
        content = creator.build_content()
        self.assertIn("class Tools:", content)
        self.assertNotIn("PLACEHOLDER_QUESTION_BANK", content)
        self.assertIn("CX-001", content)
        self.assertIn("MM-007", content)

    def test_creator_rejects_incomplete_bank(self):
        original = creator.BANK
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
                json.dump({"questions": [{"id": "X"}]}, fh)
                creator.BANK = Path(fh.name)
            with self.assertRaises(RuntimeError):
                creator.build_content()
        finally:
            creator.BANK = original

    def test_creator_payload_matches_tool(self):
        bank_size = len(bank_data["questions"])
        body = creator.payload("random_question_picker", "随机抽题工具", "class Tools:", bank_size)
        self.assertEqual(body["id"], "random_question_picker")
        self.assertEqual(body["name"], "随机抽题工具")
        self.assertIn(str(bank_size), body["meta"]["description"])


if __name__ == "__main__":
    unittest.main()
